# -*- coding: utf-8 -*-
import arrow
import time

from sqlalchemy_imageattach.context import store_context
from torgen.base import TemplateHandler
from torgen.list import ListHandler

from echsu.forms import MessageForm, CreateThreadForm
from manage.models import Board, Message, Thread
from settings import store
from toolz.base_cls import BoardDataMixin, FormMixin


class MainPageView(BoardDataMixin, TemplateHandler):
    template_name = 'main_page.html'


class MessageAdding(FormMixin):
    def make_message(self, form=None, thread_id=None):
        with store_context(store):
            message = Message(ip_address=self.request.headers.get("X-Real-IP") or self.request.remote_ip,
                              thread_id=thread_id)
            form.populate_obj(message)
            message.thread_id = thread_id
            if self.request.files.get(form.image.name, None):
                image = self.request.files[form.image.name][0]
                message.picture.from_blob(image['body'])
                message.picture.generate_thumbnail(width=150)
            message.before_added()
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            message.thread.bumped = int(round(time.time() * 1000))
            self.db.commit()
            return message

    def get_board(self):
        return self.db.query(Board).filter(Board.dir == self.path_kwargs.get('board_dir', None)).first()

    def get_form_kwargs(self):
        kwargs = super(MessageAdding, self).get_form_kwargs()
        kwargs.update({
            'board': self.get_board(),
        })
        return kwargs


class ThreadView(BoardDataMixin, MessageAdding, TemplateHandler):
    template_name = 'thread.html'
    form_class = MessageForm
    form_context_name = 'message_form'

    def get_context_data(self, **kwargs):
        board = self.db.query(Board).filter(Board.dir == self.path_kwargs.get('board_dir', None)).first()
        op_message = self.db.query(Message).filter(Message.id == self.path_kwargs.get('op_message_id', None)).first()
        context = super(self.__class__, self).get_context_data(**kwargs)
        context.update({
            'board': board,
            'thread': op_message.thread,
        })
        return context

    def form_invalid(self, form):
        return self.render(self.get_context_data(message_form=form))

    def form_valid(self, form):
        op_message = self.db.query(Message). \
            filter(Message.id == self.path_kwargs.get('op_message_id', None)).first()
        self.make_message(form=form, thread_id=op_message.thread.id)
        return self.redirect(self.reverse_url('thread', self.path_kwargs.get('board_dir', None), op_message.id))


class BoardView(BoardDataMixin, ListHandler, MessageAdding, FormMixin):
    template_name = 'board.html'
    context_object_name = 'threads'
    model = Thread
    page_kwarg = 'page'
    form_class = CreateThreadForm

    def get_queryset(self):
        board = self.db.query(Board).filter(Board.dir == self.path_kwargs.get('board_dir', None)).first()
        try:
            assert board is not None
        except AssertionError:
            self.send_error(status_code=404)

        self.paginate_by = board.threads_on_page
        self.queryset = self.db.query(self.model).order_by(Thread.bumped.desc()).\
            filter(Thread.board_id == board.id, Thread.deleted == False)
        return super(self.__class__, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        board = self.get_board()
        board_obj = board.__dict__

        board_obj['threads'] = context.pop('threads')
        context.update({
            'board': board_obj,
            'message_form': kwargs.get('message_form')
            if kwargs.get('message_form', None) else
            MessageForm(board=board,re_captcha=self.request.arguments.get('g-recaptcha-response', None) ),
        })
        return context

    def form_valid(self, form):
        board = self.get_board()
        message_form = MessageForm(self.request.arguments, board=board)
        message_form.op_post = True
        message_form.image.data = self.request.files.get(message_form.image.name, None) is not None
        if not message_form.validate() and form.validate():
            return self.render(self.get_context_data(message_form=message_form))
        thread = self.model(board_id=board.id)
        form.populate_obj(thread)
        self.db.add(thread)
        self.db.commit()
        self.db.refresh(thread)
        self.make_message(form=message_form, thread_id=thread.id)
        self.redirect(self.get_success_url())

    def get_success_url(self):
        return self.reverse_url('board', self.path_kwargs.get('board_dir', None))
