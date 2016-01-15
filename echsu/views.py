# -*- coding: utf-8 -*-
from sqlalchemy_imageattach.context import store_context
from torgen.base import TemplateHandler
from torgen.edit import FormHandler
from torgen.list import ListHandler

from echsu.forms import MessageForm, CreateThreadForm
from manage.models import Board, Message, Thread
from settings import store


class MainPageView(TemplateHandler):
    template_name = 'main_page.html'


class ThreadView(FormHandler):
    template_name = 'thread.html'
    form_class = MessageForm

    def get_context_data(self, **kwargs):
        board = self.db.query(Board).filter(Board.dir == self.path_kwargs.get('board_dir', None)).first()
        op_message = self.db.query(Message).filter(Message.id == self.path_kwargs.get('op_message_id', None)).first()
        context = super(self.__class__, self).get_context_data(**kwargs)

        context.update({
            'board': board,
            'thread': op_message.thread,
            'message_form': MessageForm()
        })
        return context

    def post(self, *args, **kwargs):
        form = self.form_class(self.request.arguments)
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
            self.db.commit()
        return self.render(self.get_context_data())


class BoardView(ListHandler):
    template_name = 'board.html'
    context_object_name = 'threads'
    paginate_by = 10
    model = Thread

    def get_queryset(self):
        board = self.db.query(Board).filter(Board.dir == self.path_kwargs.get('board_dir', None)).first()
        self.queryset = self.db.query(self.model).filter(Thread.board_id == board.id)
        return super(self.__class__, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        board = self.db.query(Board).filter(Board.dir == self.path_kwargs.get('board_dir', None)).first()
        context.update({
            'board': board,
            'message_form': MessageForm(),
            'form': CreateThreadForm(),
            'create_thread': True,
        })
        return context

    def form_valid(self):
        return self.render(self.get_context_data())

    def post(self, *args, **kwargs):
        board = self.db.query(Board).filter(Board.dir == self.path_kwargs.get('board_dir', None)).first()
        thread_form = CreateThreadForm(self.request.arguments)  # гипотетически это можно...
        message_form = MessageForm(self.request.arguments)  # запихать в одну форму
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
            self.db.add(message)
            self.db.commit()
            # except:
            #     self.db.rollback()

        return self.form_valid()
