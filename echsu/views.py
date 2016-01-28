# -*- coding: utf-8 -*-
import random
import smtplib
import string
import urllib

import arrow
import time

import os
from sqlalchemy.orm import load_only
from sqlalchemy_imageattach.context import store_context
from torgen.base import TemplateHandler
from torgen.list import ListHandler
from tornado import gen

from echsu.forms import MessageForm, CreateThreadForm, RegForm1, RegBoard
from manage.dynamic_form_fields import BoardDynamicForm
from manage.models import Board, Message, Thread, Staff, RegisterRequest
from settings import store, STATIC_PATH
from settings_local import email_settings
from toolz.get_images.bing import get_images
from toolz.base_cls import BoardDataMixin, FormMixin
from toolz.recaptcha import RecaptchaField


class MainPageView(BoardDataMixin, TemplateHandler):
    template_name = 'main_page.html'


class MessageAdding(FormMixin):
    form_class = MessageForm
    form_context_name = 'message_form'

    def make_message(self, form=None, thread_id=None):
        board = self.get_board()
        with store_context(store):
            messages_count = self.db.query(Message).filter(Message.board_id == board.id).count()
            message = Message(ip_address=self.request.headers.get("X-Real-IP") or self.request.remote_ip,
                              thread_id=thread_id, board=board, id=messages_count + 1)
            form.populate_obj(message)
            image = None
            try:
                if self.request.files.get(form.image.name, None):
                    image = self.request.files[form.image.name][0]
                    image = image['body']
                elif form.picrandom.data:
                    kw = lambda m: " ".join([random.choice(m.split(' ')), random.choice(m.split(' '))])
                    key_words = kw(form.message.data) if form.message.data\
                                        else ''.join(random.choice(string.ascii_lowercase) for x in range(2))
                    images = get_images(key_words)
                    url = random.choice(images['d']['results'])['MediaUrl']
                    image = urllib.urlopen(url).read()
                    if image is not None:
                        message.picture.from_blob(image)
                        message.picture.generate_thumbnail(width=150)
            except IndexError:
                self.db.rollback()
                if form.op_post:
                     #Если Оп-пост то отдаем картинку из локальной папки с пикчами (ну а хули?)
                    image = random.choice(os.listdir('%s/images/randpics' % STATIC_PATH))
                    message.picture.from_blob(open('%s/images/randpics/%s' % (STATIC_PATH, image), 'rb').read())
                    message.picture.generate_thumbnail(width=150)

            message.before_added(self.get_board())
            message.datetime = arrow.utcnow()
            message.thread_id = thread_id
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            if not form.sage.data:
                message.thread.bumped = int(round(time.time() * 1000))
            self.db.commit()
            return message

    def get_board(self):
        return self.db.query(Board).filter(Board.dir == self.path_kwargs.get('board_dir', None)).first()

    def get_form(self, form_class):
        board = self.get_board()
        try:
            if board.captcha:
                setattr(form_class, 'captcha', RecaptchaField(u'Капча'))
            else:
                delattr(form_class, 'captcha')
        except AttributeError:
            pass
        form = self.form_class(**self.get_form_kwargs())
        return form

    def prepare(self, **kwargs):
        board = self.get_board()
        try:
            assert board is not None
        except AssertionError:
            self.send_error(status_code=404)
        if not board.good_time():
            self.template_name = 'timer.html'
            self.render({'board': board,
                         'start': board.get_time_arrow(name='start')})
        return super(MessageAdding, self).prepare(**kwargs)

    def post(self, *args, **kwargs):
        self.form_class.image_attached = self.request.files.get('image', None) is not None
        self.form_class.op_post = self.__class__ is BoardView
        return super(MessageAdding, self).post(args, kwargs)

    def form_invalid(self, form):
        context = self.get_context_data(message_form=form)
        context[self.form_context_name] = form
        return self.render(context)


class ThreadView(BoardDataMixin, MessageAdding, TemplateHandler):
    template_name = 'thread.html'

    def get_thread(self):
        board = self.get_board()
        op = self.db.query(Message).options(load_only('thread_id')) \
            .filter(Message.board_id == board.id, Message.id == self.path_kwargs.get('op_message_id', None)).first()
        return op.thread

    def get_context_data(self, **kwargs):
        thread = self.get_thread()
        context = super(self.__class__, self).get_context_data(**kwargs)
        context.update({
            'board': thread.board,
            'thread': thread,
        })
        return context

    def form_valid(self, form):
        thread = self.get_thread()
        self.make_message(form=form, thread_id=thread.id)
        return self.redirect(self.reverse_url('thread', self.path_kwargs.get('board_dir', None), thread.op().id))


class BoardView(BoardDataMixin, ListHandler, MessageAdding):
    template_name = 'board.html'
    context_object_name = 'threads'  # board.threads
    model = Thread
    page_kwarg = 'page'

    def get_queryset(self):
        board = self.get_board()
        self.paginate_by = board.threads_on_page
        self.queryset = self.db.query(self.model).join(Message).\
            filter(Thread.board_id == board.id, Thread.deleted == False).order_by(Thread.bumped.desc())
        return super(self.__class__, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['board'] = self.get_board().__dict__
        context['board']['threads'] = context.pop('threads')
        return context

    def form_valid(self, form):
        board = self.get_board()
        thread_form = CreateThreadForm(self.request.arguments, board=board)
        thread = self.model(board_id=board.id)
        thread_form.populate_obj(thread)
        self.db.add(thread)
        self.db.commit()
        self.db.refresh(thread)
        try:
            self.make_message(form=form, thread_id=thread.id)
        except:
            pass
        self.redirect(self.get_success_url())

    def get_success_url(self):
        return self.reverse_url('board', self.get_board().dir)


class RegisterModerator(BoardDataMixin, TemplateHandler, FormMixin):
    """
        Не ну а чо? Анонимный имиджборд же!
    """
    form_class = RegForm1
    model = Staff
    template_name = 'registration/registration_step_1.html'

    def form_valid(self, form):
        super(RegisterModerator, self).form_valid(form)
        rr = RegisterRequest(staff=self.object)
        self.db.add(rr)
        self.db.commit()
        self.db.refresh(rr)

        toaddr = form.email.data
        subj = 'Notification from system'
        link = 'https://ech.su%s' % (self.reverse_url('reg2', rr.hash))
        msg_txt = u'Для того чтобы создать доску пройди по ссылке:\n\n ' + link + \
                  u'\n\nАккаунт модератора, будет доступен после создания доски!'  #
        msg = u"From: %s\nTo: %s\nSubject: %s\n\n%s" % (email_settings['from'], toaddr, subj, msg_txt)
        server = smtplib.SMTP(email_settings['smtp'])
        server.starttls()
        server.login(email_settings['username'], email_settings['password'])
        server.sendmail(email_settings['from'], toaddr, msg.encode('utf-8'))
        server.quit()

        self.template_name = '/registration/step1_success.html'
        self.render({'email': form.email.data})


class RegisterBoard(BoardDataMixin, TemplateHandler, BoardDynamicForm, FormMixin):
    """
        Чем больше сделают другие, тем меньше далать самому!
    """
    form_class = RegBoard
    model = Board
    template_name = 'registration/registration_step_2.html'
    success_url = '/'

    def get_request(self):
        return self.db.query(RegisterRequest).filter(RegisterRequest.hash == self.path_kwargs.get('key', None)).first()

    def prepare(self):
        valid_request = self.get_request()
        if not valid_request:
            raise self.send_error(status_code=403)

    def form_valid(self, form):
        super(RegisterBoard, self).form_valid(form)
        request = self.get_request()
        request.staff.active = True
        request.staff.boards.append(self.object)
        self.db.query(RegisterRequest.id == request.id).delete()
        self.db.commit()
        return self.redirect(self.get_success_url())
