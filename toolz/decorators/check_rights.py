from manage.models import Message


def admin_only(cls, methods=['prepare']):
    def decorator(fn):
        def tmp(self, *args, **kw):
            if self.current_user and self.current_user.is_admin():
                return fn(self, *args, **kw)
            else:
                self.send_error(status_code=403)
        return tmp
    for method in methods:
        setattr(cls, method, decorator(getattr(cls, method)))
    return cls


def login_required(cls, methods=['prepare']):
    def decorator(fn):
        def tmp(self, *args, **kw):
            if self.current_user:
                return fn(self, *args, **kw)
            else:
                self.send_error(status_code=403)
        return tmp
    for method in methods:
        setattr(cls, method, decorator(getattr(cls, method)))
    return cls


def can_moderate(cls, method='prepare'):
    def decorator(fn):
        def closure(self, *args, **kwargs):
            board_id = self.path_kwargs.get('id', None)
            if board_id is None:
                message_id = self.path_kwargs.get('gid', None)
                if message_id is not None:
                    mes = self.db.query(Message).filter(Message.gid == message_id).first()
                    board_id = mes.board.id
            can_moderate = reduce(lambda x, y: x or y,
                           [self.current_user.check_moderate(board_id),
                            self.current_user.all_boards,
                            self.current_user.is_admin()], False)
            if not can_moderate:
                self.send_error(status_code=403)
        return closure
    setattr(cls, method, decorator(getattr(cls, method)))
    return cls