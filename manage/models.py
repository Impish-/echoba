# -*- coding: utf-8 -*-

from sqlalchemy import String, Integer, ForeignKey, BOOLEAN, Table, UnicodeText
from sqlalchemy_defaults import Column
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship, backref
from sqlalchemy_imageattach.entity import image_attachment, Image
from sqlalchemy_utils import PasswordType, ChoiceType, IPAddressType

from toolz.base_models import SessionMixin
from toolz.bd_toolz import with_session, engine

Base = declarative_base()

mod_rights = Table('association', Base.metadata,
    Column('staff_id', Integer, ForeignKey('staff.id')),
    Column('board_id', Integer, ForeignKey('board.id'))
)


class Staff(Base, SessionMixin):
    name = Column(String, unique=True)
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
                             ]), nullable=False
    )
    all_boards = Column(BOOLEAN, default=False)
    boards = relationship("Board",
                          secondary=mod_rights,
                          backref=backref('staff', lazy='dynamic',),
                          passive_deletes=True,
                          passive_updates=False)

    def __init__(self, name, password, role):
        self.name = name
        self.password = password
        self.role = role

    def __repr__(self):
        return "<User('%s', '%s', %s)>" % (self.name, self.password, self.role)


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
        return Staff(name, password, role).save()

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
    def add_mod_rights(self, board, session=None):
        self.boards.append(board)
        session.commit()


class Board(Base, SessionMixin):
    name = Column(String, unique=True, label=u'Название')
    dir = Column(String, unique=True, label=u'Директория')
    threads_on_page = Column(Integer, default=9, label=u'Тредов на странице')
    default_name = Column(String, default=u'Anonymouse', label=u'Имя постера')
    max_pages = Column(Integer, default=11, label=u'Максимальное кол-во страниц')
    thread_bumplimit = Column(Integer, default=500, label=u'Бамплимит')
    thread_tail = Column(Integer, default=5, label=u'Хвост треда(сообщений на странице)')
    captcha = Column(BOOLEAN, default=False, label=u'Капча')
    #threads = relationship('Thread', backref=backref('board', lazy='dynamic',),)

    #TODO: выпилить, model_form.populate_obj юзать
    def __init__(self, **kwargs):
        # в случае получения id  в kwargs вытягивать из бд объект
        self.name = kwargs.get('name', None)
        self.dir = kwargs.get('dir', None)
        self.threads_on_page = kwargs.get('threads_on_page', None)
        self.default_name = kwargs.get('default_name', None)
        self.max_pages = kwargs.get('max_pages', None)
        self.thread_bumplimit = kwargs.get('thread_bumplimit', None)
        self.thread_tail = kwargs.get('thread_tail', None)
        self.captcha = kwargs.get('captcha', None)

    def __repr__(self):
        return "<Board('%s')>" % (self.dir)

    @with_session
    def add_moderator(self, staff_id, session=None):
        self.staff.append(session.query(Staff).filter(Staff.id == staff_id).first())
        session.commit()

    @with_session
    def remove_moderator(self, staff_id, session=None):
        staff = session.query(Staff).filter(Staff.id == staff_id).first()
        staff.remove_mod_rights(self)
        session.commit()


    # @declared_attr
    # @with_session
    # def threads(self, session=None):
    #     return session.query(Thread).filter(Thread.board_id == self.id).all()

    @staticmethod
    @with_session
    def create(name, dir, session=None):
        return Board(name=name, dir=dir).add()

    @staticmethod
    @with_session
    def remove_board(name, session):
        session.query(Board).filter(Board.name == name).delete(synchronize_session=False)
        session.commit()

    @staticmethod
    @with_session
    def get_all(session):
       return session.query(Board).all()

    @staticmethod
    @with_session
    def get_board(id=None, dir=None, session=None):
        try:
            if id:
                return session.query(Board).filter(Board.id == id).first()
            if dir:
                return session.query(Board).filter(Board.dir == dir).first()
        except:
            return None


class Thread(Base, SessionMixin):
    sticky = Column(BOOLEAN, label=u'Прикреплен', default=False)
    closed = Column(BOOLEAN, label=u'Закрыт', default=False)
    messages = relationship("Message", lazy='subquery', cascade='all, delete-orphan',
                            backref=backref('thread'), )

    board_id = Column(Integer, ForeignKey('board.id'), primary_key=True)

    board = relationship('Board', lazy='subquery', cascade='all',
                         backref=backref('threads', lazy='dynamic', cascade='all', ))

    def op(self):
        return self.messages[0]

    def messages_tail(self, session=None):
        return self.messages[1:][-self.board.thread_tail:]

    @staticmethod
    @with_session
    def get_threads(board_id, session=None):
        return session.query(Thread).filter(board_id).all()

    @with_session
    def remove(self, session):
        session.query(Thread).filter(Thread.id == self.id).delete(synchronize_session=False)
        session.commit()


class Message(Base, SessionMixin):
    poster_name = Column(String, label=u'Имя', nullable=True)
    email = Column(String, label=u'E-Mail', nullable=True)
    header = Column(String, label=u'Заголовок', nullable=True)
    message = Column(UnicodeText, label=u'Сообщение')
    picture = image_attachment('BoardPicture')
    password = Column(PasswordType(
                schemes=[
                    'pbkdf2_sha512',
                    'md5_crypt'
                ],

                deprecated=['md5_crypt']), label=u'Пароль(для удаления поста)')
    thread_id = Column(Integer, ForeignKey('thread.id'), primary_key=True)
    #
    #mod_hash = Хэшкод модератора
    #mad_action = список действий модератора(подписаться,создать прикрепленный/закрытый тред, row_html, другая еба)
    ip_address = Column(IPAddressType)
    image = image_attachment('BoardImage')

    def __repr__(self):
        return "<Message('id=%s')>" % (self.id)

    def thumbnail(self):
        # Make thumbnails
        width_150 = self.picture.generate_thumbnail(width=150)
        height_300 = self.picture.generate_thumbnail(height=300)
        half = self.picture.generate_thumbnail(ratio=0.5)
        # Get their urls
        width_150_url = width_150.locate()
        height_300_url =height_300.locate()
        half = half.locate()
        return half

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

    message_id = Column(Integer, ForeignKey('message.id'), primary_key=True,)
    message = relationship('Message')