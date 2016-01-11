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
    model = Message

    def get(self,*args, **kwargs):
        board = Board.get_board(dir=self.path_kwargs.get('board_dir',None))
        for x in board.threads.all():
            print(x.op())
            print(x.messages_tail())
        self.render_template(board=board, threads=board.threads.all()) if board else self.send_error(status_code=404)

    #надо доаутировать
    def post(self, *args, **kwargs):
        board = Board.get_board(dir=self.path_kwargs.get('board_dir', None))
        thread_form = self.get_form()
        message_form = MessageForm(self.request.arguments)
        # if not thread_form.validate():
        #     #!
        #     return self.render_template(board=Board.get_board(dir=self.path_kwargs.get('board_dir', None)))


        thread = Thread()

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

    def get(self, board_dir, thread_id):
        board = self.get_board(board_dir)
        thread = Thread.query.get(op_id=int(thread_id))
        thread.t_messages = self.get_messages(thread.op_id, 0)
        self.render_template('templates/thread.html', board=board, cur_thread=thread) \
            if board and thread else self.send_error(status_code=404)

