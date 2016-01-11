# -*- coding: utf-8 -*-
from jinja2 import Environment, PackageLoader

from echsu.forms import MessageForm, CreateThreadForm
from manage.models import Board, Message, Thread
from toolz.base_cls import BaseHandler


# TODO: автоматизировать как-то под каждое приложение
template_env = Environment(loader=PackageLoader('echsu', 'templates'))


class MainPageView(BaseHandler):
    template = 'main_page.html'
    template_env = template_env

    def get(self, *args, **kwargs):
        self.render_template()


class BoardView(BaseHandler):
    template = 'board.html'
    template_env = template_env
    form = CreateThreadForm
    model = Thread

    def get(self,*args, **kwargs):
        board = Board.get_board(dir=self.path_kwargs.get('board_dir',None))
        self.render_template(board=board, threads=board.threads) if board else self.send_error(status_code=404)

    #надо доаутировать
    def post(self, *args, **kwargs):
        # Тут создается тренд
        board = Board.get_board(dir=self.path_kwargs.get('board_dir', None))

        thread_form = self.get_form()                       # гипотетически это можно...
        message_form = MessageForm(self.request.arguments)  # запихать в одну форму

        if not message_form.validate() and thread_form.validate():             # таки утрамбовать в Board класс
            return self.render_template(board=board,
                                        threads=board.threads.all(),
                                        message_form=message_form)

        thread = self.model()
        thread.board_id = board.id
        thread_form.populate_obj(thread)
        thread.save()

        message = Message()
        message_form.populate_obj(message)
        message.ip_address = self.request.headers.get("X-Real-IP") or self.request.remote_ip
        message.thread_id = thread.id
        message.save()

        return self.render_template(board=Board.get_board(dir=self.path_kwargs.get('board_dir', None)))

    def get_context(self):
        context = super(self.__class__, self).get_context()
        context.update({'message_form': MessageForm()})
        return context


class ThreadView(BaseHandler):
    template_env = template_env
    template = 'thread.html'
    form = MessageForm
    form_context_name = 'message_form'

    def get(self, *args, **kwargs):
        board = Board.get_board(dir=kwargs.get('board_dir', None))
        op_message = Message.get_message(kwargs.get('id_op_message', None))


        print board
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
        message.save()

        return self.render_template(board=board,
                                    thread=op_message.thread,)



