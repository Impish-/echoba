from tornado.web import RequestHandler


class MainPageView(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('templates/main_page.html')


class ThreadView(RequestHandler):
    def get(self, board_dir, thread_id):
        board = self.get_board(board_dir)
        thread = Thread.query.get(op_id=int(thread_id))
        thread.t_messages = self.get_messages(thread.op_id, 0)
        self.render('templates/thread.html', board=board, cur_thread=thread)\
            if board and thread else self.send_error(status_code=404)


class BoardView(RequestHandler):
    def get(self, board_dir):
        board = self.get_board(board_dir)

        def prepare_thread(thread):
            thread.t_messages = self.get_messages(thread.op_id, 0)
            thread.op_message = Message.Api.get_message(thread.op_id)
            return thread

        threads = [prepare_thread(thread) for thread in Thread.Api.get_for_board(board.dir if board else None)]
        self.render('templates/board.html', board=board, threads=threads, cur_thread=None) if board else self.send_error(status_code=404)
