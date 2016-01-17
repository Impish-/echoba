# -*- coding: utf-8 -*-
import arrow
import time

from sqlalchemy import desc
from sqlalchemy_imageattach.context import store_context
from torgen.base import TemplateHandler
from torgen.edit import FormHandler
from torgen.list import ListHandler

from echsu.forms import MessageForm, CreateThreadForm
from manage.models import Board, Message, Thread
from settings import store
from toolz.base_cls import BoardDataMixin


class MainPageView(BoardDataMixin, TemplateHandler):
    template_name = 'main_page.html'


class ThreadView(BoardDataMixin, FormHandler):
    template_name = 'thread.html'
    form_class = MessageForm

    def get_context_data(self, **kwargs):
        board = self.db.query(Board).filter(Board.dir == self.path_kwargs.get('board_dir', None)).first()
        op_message = self.db.query(Message).filter(Message.id == self.path_kwargs.get('op_message_id', None)).first()
        context = super(self.__class__, self).get_context_data(**kwargs)

        context.update({
            'board': board,
            'thread': op_message.thread,
            'message_form': kwargs.get('message_form') if kwargs.get('message_form', None) else MessageForm(),
            'form': [],
        })
        return context

    def post(self, *args, **kwargs):
        self.kwargs = kwargs
        form = self.form_class(self.request.arguments)
        form.image.data = self.request.files.get(form.image.name, None) is not None
        return self.form_valid(form) if form.validate() else self.form_invalid(form)

    def form_invalid(self, form):
        return self.render(self.get_context_data(message_form=form))

    def form_valid(self, form):
        op_message = self.db.query(Message).\
            filter(Message.id == self.path_kwargs.get('op_message_id', None)).first()
        with store_context(store):
            message = Message()
            form.populate_obj(message)
            message.thread_id = op_message.thread.id
            if self.request.files.get(form.image.name, None):
                image = self.request.files[form.image.name][0]
                message.picture.from_blob(image['body'])
                message.picture.generate_thumbnail(width=150)

            self.db.add(message)
            if not form.sage.data:
                op_message.thread.bumped =int(round(time.time() * 1000))
            self.db.add(message)
            self.db.commit()
        return self.render(self.get_context_data())


class BoardView(BoardDataMixin, ListHandler):
    template_name = 'board.html'
    context_object_name = 'threads'
    paginate_by = 10
    model = Thread

    def get_queryset(self):
        board = self.db.query(Board).filter(Board.dir == self.path_kwargs.get('board_dir', None)).first()
        self.queryset = self.db.query(self.model).order_by(Thread.bumped.desc()).filter(Thread.board_id == board.id)
        return super(self.__class__, self).get_queryset()

    def get_context_data(self, **kwargs):
        self.object_list = self.get_queryset()
        context = super(self.__class__, self).get_context_data(**kwargs)
        board = self.db.query(Board).filter(Board.dir == self.path_kwargs.get('board_dir', None)).first()

        board_obj = {
            'dir': board.dir,
            'name': board.name,
            'threads': context.pop('threads')
        }

        context.update({
            'board': board_obj,
            'message_form': kwargs.get('message_form') if kwargs.get('message_form', None) else MessageForm(),
            'form': CreateThreadForm(),
        })
        return context

    def post(self, *args, **kwargs):
        self.kwargs = kwargs
        board = self.db.query(Board).filter(Board.dir == self.path_kwargs.get('board_dir', None)).first()
        thread_form = CreateThreadForm(self.request.arguments)  # гипотетически это можно...
        message_form = MessageForm(self.request.arguments)  # запихать в одну форму
        message_form.op_post = True
        message_form.image.data = self.request.files.get(message_form.image.name, None) is not None
        if not message_form.validate() and thread_form.validate():
            return self.render(self.get_context_data(message_form=message_form))

        thread = self.model(board_id=board.id)
        thread_form.populate_obj(thread)
        self.db.add(thread)
        self.db.commit()
        self.db.refresh(thread)
        # try:
        with store_context(store):
            message = Message(ip_address=self.request.headers.get("X-Real-IP") or self.request.remote_ip,
                              thread_id=thread.id)
            message_form.populate_obj(message)
            if self.request.files.get(message_form.image.name, None):
                image = self.request.files[message_form.image.name][0]
                message.picture.from_blob(image['body'])
                message.picture.generate_thumbnail(width=150)
            thread.bumped = int(round(time.time() * 1000))
            self.db.add(message)
            self.db.commit()
            # except:
            #     self.db.rollback()
        return super(ListHandler, self).get(args, kwargs)

