# -*- coding: utf-8 -*-
from sqlalchemy import String, Integer, ForeignKey, BOOLEAN, Table, UnicodeText, BigInteger
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy_defaults import Column
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship, backref
from sqlalchemy_imageattach.context import store_context
from sqlalchemy_imageattach.entity import image_attachment, Image
from sqlalchemy_utils import PasswordType, ChoiceType, IPAddressType, ArrowType

from settings import store
from toolz.base_models import SessionMixin
from toolz.bd_toolz import with_session

import arrow
import re

from tripcode import tripcode

Base = declarative_base()

mod_rights = Table('association', Base.metadata,
                   Column('id', Integer, primary_key=True),
                   Column('staff_id', Integer, ForeignKey('staff.id')),
                   Column('board_id', Integer, ForeignKey('board.id'))
                   )


class Staff(Base, SessionMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, label=u'Юзернэйм')
    password = Column(PasswordType(
            schemes=[
                'pbkdf2_sha512',
                'md5_crypt',
            ],
            deprecated=['md5_crypt'],
    ), nullable=False
    )
    role = Column(ChoiceType([('adm', u'Admin'),
                              ('mod', u'Moderator'),
                              ]), nullable=False, label=u'Роль'
                  )
    all_boards = Column(BOOLEAN, default=False, label=u'Модератор всех досок')
    boards = relationship("Board", load_on_pending=True,
                          secondary=lambda: mod_rights,
                          backref=backref('staff', lazy='dynamic', load_on_pending=True), )

    def __repr__(self):
        return "<User '%s' - (%s)(id='%d')>" % (self.name, self.role, self.id)

    @declared_attr
    def is_admin(self):
        return self.role == 'adm'

    @staticmethod
    @with_session
    def get_auth(name, password, session=None):
        user = session.query(Staff).filter(Staff.name == name).first()
        try:
            return user if user.password == password else None
        except AttributeError:
            return None

    @staticmethod
    @with_session
    def create_user(name, password, role, session=None):
        session.expire_on_commit = False
        user = Staff()
        user.name = name
        user.password = password
        user.role = role
        user.add()
        return user

    @staticmethod
    @with_session
    def update_user(name, password, role, id, session=None):
        user = session.query(Staff).filter(Staff.id == id).first()
        session.expire_on_commit = False
        if name:
            user.name = name
        if password:
            user.password = password
        if role:
            user.role = role
        session.commit()
        return user

    @staticmethod
    @with_session
    def get_user(name, session):
        return session.query(Staff).filter(Staff.name == name).first()

    @staticmethod
    @with_session
    def get_user_by_id(id, session):
        return session.query(Staff).filter(Staff.id == id).first()

    @staticmethod
    @with_session
    def remove_user(name, session):
        user = session.query(Staff).filter(Staff.name == name).first()
        try:
            user.boards[:] = []
        except AttributeError:
            pass
        session.query(Staff).filter(Staff.name == name).delete(synchronize_session=False)
        session.commit()

    @staticmethod
    @with_session
    def get_users(session):
        return session.query(Staff).all()

    @with_session
    def remove_mod_rights(self, board, session=None):
        for s_board in self.boards:
            if s_board.id == board.id:
                self.boards.remove(s_board)
        session.commit()

    @with_session
    def add_mod_rights(self, board_id, session=None):
        board = Board.get_board(id=board_id)
        self.boards.append(board)
        self.save()
        session.commit()


bans = Table('ban_table', Base.metadata,
             Column('id', Integer, primary_key=True),
             Column('ban_id', Integer, ForeignKey('ban.id')),
             Column('board_id', Integer, ForeignKey('board.id'))
             )


class Ban(Base, SessionMixin):
    created_by = relationship('Staff',
                              backref=backref('bans', lazy="subquery"))
    staff_id = Column(Integer, ForeignKey('staff.id'))
    created_at = Column(ArrowType, default=arrow.utcnow())
    end = Column(ArrowType, default=arrow.utcnow())
    ip = Column(IPAddressType)
    boards = relationship("Board", load_on_pending=True,
                      secondary=lambda: bans,
                      backref=backref('ban_list', lazy='dynamic', load_on_pending=True), )


class Section(Base, SessionMixin):
    name = Column(String, unique=True, label=u'Название Раздела')

    @staticmethod
    @with_session
    def get_all(session):
        return session.query(Section).all()


class Board(Base, SessionMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, label=u'Название')
    dir = Column(String, unique=True, label=u'Директория')
    threads_on_page = Column(Integer, default=9, label=u'Тредов на странице')
    default_name = Column(String, default=u'Anonymouse', label=u'Имя постера')
    max_pages = Column(Integer, default=11, label=u'Максимальное кол-во страниц')
    thread_bumplimit = Column(Integer, default=500, label=u'Бамплимит')
    thread_tail = Column(Integer, default=5, label=u'Хвост треда(сообщений на странице)')
    captcha = Column(BOOLEAN, default=False, label=u'Капча')
    section = relationship('Section',
                           backref=backref('boards', lazy="subquery"))
    section_id = Column(Integer, ForeignKey('section.id'))

    def __repr__(self):
        return "<Board('%s')>" % (self.dir)

    @with_session
    def add_moderator(self, staff_id, session=None):
        self.staff.append(session.query(Staff).get(staff_id))
        session.commit()

    @with_session
    def remove_moderator(self, staff_id, session=None):
        staff = session.query(Staff).get(staff_id)
        staff.remove_mod_rights(self)
        session.commit()

    # @declared_attr
    # @with_session
    # def threads(self, session=None):
    #     return session.query(Thread).filter(Thread.board_id == self.id).all()

    @staticmethod
    def create(name, dir):
        board = Board()
        board.name = name,
        board.dir = dir,
        board.add()
        return board

    @staticmethod
    @with_session
    def remove_board(name, session):
        try:
            session.query(Board).filter(Board.name == name).delete(synchronize_session=False)
            session.commit()
        except:
            pass

    @staticmethod
    @with_session
    def get_all(session):
        return session.query(Board).all()

    @staticmethod
    @with_session
    def get_board(id=None, dir=None, session=None):
        try:
            board = None
            if id:
                board = session.query(Board).filter(Board.id == id).first()
            elif dir:
                board = session.query(Board).filter(Board.dir == dir).first()
            return board
        except:
            return None


class Thread(Base, SessionMixin):
    id = Column(Integer, primary_key=True)
    sticky = Column(BOOLEAN, label=u'Прикреплен', default=False)
    closed = Column(BOOLEAN, label=u'Закрыт', default=False)
    messages = relationship("Message", lazy='subquery', cascade='all, delete-orphan', order_by="Message.gid",
                            backref=backref('thread'),
                            primaryjoin="and_(Message.deleted==False, Message.thread_id==Thread.id)")

    board_id = Column(Integer, ForeignKey('board.id'), primary_key=True)

    board = relationship('Board', lazy='subquery', cascade='all',
                         backref=backref('threads', lazy='dynamic', cascade='all, delete-orphan'))

    bumped = Column(BigInteger)
    deleted = Column(BOOLEAN, default=False)

    def op(self):
        try:
            return self.messages[0]
        except IndexError:
            return []

    def messages_tail(self, session=None):
        return self.messages[1:][-self.board.thread_tail:]

    def left(self):
        left = len(self.messages) - (self.board.thread_tail + 1)
        return left if left > 0 else None

    def link(self):
        try:
            return '/%s/%d/' % (self.board.dir, self.op().id)
        except AttributeError:
            return ''

    @staticmethod
    @with_session
    def get_threads(board_id, session=None):
        return session.query(Thread).filter(board_id).all()

    @with_session
    def remove(self, session):
        session.query(Thread).filter(Thread.id == self.id).delete(synchronize_session=False)
        session.commit()


class Message(Base, SessionMixin):
    id = Column(Integer, nullable=False)
    gid = Column(Integer, primary_key=True)
    poster_name = Column(String, label=u'Имя', nullable=True)
    email = Column(String, label=u'E-Mail', nullable=True)
    header = Column(String, label=u'Заголовок', nullable=True)
    message = Column(UnicodeText, label=u'Сообщение', nullable=True)
    picture = image_attachment('BoardImage')
    password = Column(PasswordType(
            schemes=[
                'pbkdf2_sha512',
                'md5_crypt'
            ],

            deprecated=['md5_crypt']), label=u'Пароль')
    thread_id = Column(Integer, ForeignKey('thread.id'), primary_key=True)

    ip_address = Column(IPAddressType)
    datetime = Column(ArrowType, default=arrow.utcnow())
    deleted = Column(BOOLEAN, default=False)

    board_id = Column(Integer, ForeignKey('board.id'), primary_key=True)
    board = relationship('Board', backref=backref('messages', ))


    # image = image_attachment('BoardImage')

    def __repr__(self):
        return "<Message: %s>" % (self.id)

    def img_thumb(self):
        '''
            миниатюра(по идее в настройках борды будут задаваться размеры)
        '''
        with store_context(store):
            try:
                return self.picture.find_thumbnail(width=150).locate()
            except NoResultFound:
                return None

    def image_info(self):
        '''
            Полноразмерное изображение
        '''
        with store_context(store):
            locate = self.picture.locate()
            return {
                'locate': locate,
                'name': locate.split('/')[-1].split('?')[0],
                'width': self.picture.original.width,
                'height': self.picture.original.height
            }

    @staticmethod
    def _safe_string(text):
        replaced_data = (
            ('&amp;', r'&', 0),
            ('&lt;', r'<', 0),
            ('&gt;', r'>', 0)
        )
        for (r, p, f) in replaced_data:
            text = re.sub(p, r, text, flags=f)
        return text

    @staticmethod
    @with_session
    def _formated_message(message, board, session=None):
        message = Message._safe_string(message)

        def question_callback(math):
            mess_id = math.group('var')
            board_id = board.id
            prefix = ''
            try:
                tmp_board = session.query(Board).filter(Board.dir==math.group('board')).first()
                if tmp_board is not None:
                    board_id = tmp_board.id
                    prefix = math.group('board') + '/'
            except:
                pass
            message = session.query(Message).filter(Message.id==mess_id, Message.board_id==board_id).first()
            if message is not None:
                return '<a href="%s#%s" class="ql">&gt;&gt;%s%s</a>' % (message.thread.link(), mess_id, prefix, mess_id)
            return math.group(0)

        replaced_data = (
            ('<br>\n', r'\n', 0),
            ('', r'\r', 0),
            ('&quot;', r'"', 0),
            (question_callback, r'&gt;&gt;(?P<var>\d+)', 0),
            (question_callback, r'&gt;&gt;(?P<board>[a-zA-Z0-9]+)/(?P<var>\d+)', 0),
            ('\g<begin><span class="unkfunc">&gt;\g<var></span>\g<end>',
             r'(?P<begin>^|<br>|\n)&gt;(?P<var>.*?)(?P<end><br>|$)', re.I),
            ('\g<begin><a href="\g<protocol>\g<var>">\g<protocol>\g<var></a>',
             r'(?P<begin>^|[^a-zA-Z0-9])(?P<protocol>http://|https://|ftp://)(?P<var>[^(\s<|\[)]*)', re.I),
            ('<b>\g<var></b>', r'\[b](?P<var>.*?)\[/b]', re.I),
            ('<b>\g<var></b>', r'\*\*(?P<var>.*?)\*\*', re.I),
            ('<b>\g<var></b>', r'__(?P<var>.*?)__', re.I),
            ('<i>\g<var></i>', r'\[i](?P<var>.*?)\[/i]', re.I),
            ('<i>\g<var></i>', r'\*(?P<var>.*?)\*', re.I),
            ('<i>\g<var></i>', r'_(?P<var>.*?)_', re.I),
            ('<u>\g<var></u>', r'\[u](?P<var>.*?)\[/u]', re.I),
            ('<sup>\g<var></sup>', r'\[sup](?P<var>.*?)\[/sup]', re.I),
            ('<sub>\g<var></sub>', r'\[sub](?P<var>.*?)\[/sub]', re.I),
            ('<del>\g<var></del>', r'\[s](?P<var>.*?)\[/s]', re.I),
            ('<del>\g<var></del>', r'\^(?P<var>.*?)\^', re.I),
            ('<pre>\g<var></pre>', r'\[code](?P<var>.*?)\[/code]', re.I),
            ('<pre>\g<var></pre>', r'```(?P<var>.*?)```', re.I),
            ('<span class="spoiler">\g<var></span>', r'\[spoiler](?P<var>.*?)\[/spoiler]', re.I),
            ('<span class="spoiler">\g<var></span>', r'\%\%(?P<var>.*?)\%\%', re.I),
        )
        for (r, p, f) in replaced_data:
            message = re.sub(p, r, message, flags=f)
        return message

    def before_added(self, board):
        self.message = Message._formated_message(self.message, board)
        if len(self.poster_name) > 1 and self.poster_name[0] in (u'#', u'!'):
            self.poster_name = u'<span class="postertrip">!%s</span>' % tripcode(self.poster_name[1:])
        else:
            self.poster_name = Message._safe_string(self.poster_name)

    @staticmethod
    @with_session
    def get_message(id=None, session=None):
        try:
            return session.query(Message).filter(Message.id == id).first()
        except:
            return None

    @staticmethod
    @with_session
    def get_last_messages(thread_id=None, last_message=None, session=None):
        try:
            return session.query(Message).filter(Message.id > last_message).all()
        except:
            return []


class BoardImage(Base, Image):
    __tablename__ = 'images'

    message_gid = Column(Integer, ForeignKey('message.gid'), primary_key=True, )
    message = relationship('Message')
