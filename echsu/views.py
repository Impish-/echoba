# -*- coding: utf-8 -*-
from jinja2 import Environment, PackageLoader
from sqlalchemy_imageattach.context import store_context

from echsu.forms import MessageForm, CreateThreadForm
from manage.models import Board, Message, Thread
from settings import store
from toolz.base_cls import BaseHandler


# TODO: автоматизировать как-то под каждое приложение
template_env = Environment(loader=PackageLoader('echsu', 'templates'))


class MainPageView(BaseHandler):
    template = 'main_page.html'
    template_env = template_env

    def get(self, *args, **kwargs):
        self.render_template()


class ThreadView(BaseHandler):
    template_env = template_env
    template = 'thread.html'
    form = MessageForm
    form_context_name = 'message_form'

    def get(self, *args, **kwargs):
        board = Board.get_board(dir=kwargs.get('board_dir', None))
        op_message = Message.get_message(kwargs.get('id_op_message', None))

        self.render_template(board=board, thread=op_message.thread) \
            if board else self.send_error(status_code=404)

    def post(self, *args, **kwargs):
        #тут создаются сообщения в тенд
        board = Board.get_board(dir=kwargs.get('board_dir', None))
        op_message = Message.get_message(kwargs.get('id_op_message', None))

        form = self.get_form()
        message = Message()
        form.populate_obj(message)
        message.thread_id = op_message.thread.id
        message.add()

        return self.get(*args, **kwargs)


class BoardView(BaseHandler):
    template = 'board.html'
    template_env = template_env
    form = CreateThreadForm
    model = Thread

    def get(self, *args, **kwargs):
        board = Board.get_board(dir=self.path_kwargs.get('board_dir', None))
        print board.threads # очень сильно колдунство (нужно чтобы треды в борду подгружались)- потом нормально сделаю
        self.render_template(board=board) if board else self.send_error(status_code=404)

    #надо доаутировать
    def post(self, *args, **kwargs):
        # Тут создается тренд
        board = Board.get_board(dir=self.path_kwargs.get('board_dir', None))

        thread_form = self.get_form()                       # гипотетически это можно...
        message_form = MessageForm(self.request.arguments)  # запихать в одну форму

        if not message_form.validate() and thread_form.validate():             # таки утрамбовать в Board класс
            return self.render_template(board=board,
                                        message_form=message_form)

        thread = self.model(board_id=board.id)
        thread_form.populate_obj(thread)
        thread.add()

        # кусок объеденить

        message = Message(ip_address=self.request.headers.get("X-Real-IP") or self.request.remote_ip,
                          thread_id=thread.id)
        message_form.populate_obj(message)
        message.add()

        if self.request.files.get(message_form.image.name, None):
            image = self.request.files[message_form.image.name][0]
            fname = image['filename']
            with store_context(store):
                with open("media/%s" % (fname), "w") as out:
                    out.write(image['body'])
                with open("media/%s" % (fname), 'rb') as f:
                    message.picture.from_blob(f.read())
                message.save()

            print message.picture
        return self.get(*args, **kwargs)

    def get_context(self):
        context = super(self.__class__, self).get_context()
        context.update({'message_form': MessageForm()})
        return context



