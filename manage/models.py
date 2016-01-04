# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import PasswordType, ChoiceType

from toolz.base_models import SessionMixin
from toolz.bd_toolz import with_session, engine

Base = declarative_base()


class Staff(Base, SessionMixin):
    name = Column(String, unique=True)
    password = Column(PasswordType(
                        schemes=[
                            'pbkdf2_sha512',
                            'md5_crypt',
                        ],
                        deprecated=['md5_crypt'],
                    )
    )
    role = Column(ChoiceType([('adm', u'Admin'),
                              ('mod', u'Moderator'),
                             ])
    )

    def __init__(self, name, password, role):
        self.name = name
        self.password = password
        self.role = role

    def __repr__(self):
        return "<User('%s', '%s', %s)>" % (self.name, self.password, self.role)

    @staticmethod
    @with_session
    def get_auth(name, password, session=None):
        user = session.query(Staff).filter(Staff.name == name).first()
        return user.password == password

    @staticmethod
    @with_session
    def get_or_create_user(name, password, role, session=None):
        user = session.query(Staff).filter(Staff.name == name).first()
        return user if user else Staff(name, password, role).save()


class Board(Base, SessionMixin):
    name = Column(String, unique=True)
    dir = Column(String, unique=True)
    threads_on_page = Column(Integer)
    default_name = Column(String, default='Anonymouse')
    max_pages = Column(Integer)


class Thread(Base, SessionMixin):
    id = Column(Integer, primary_key=True)
    title = Column(String)
    board = Column('board_id', Integer, ForeignKey('board.id'))
    bump_timestamp = Column(Integer)
    bump_limited = Column(Boolean)
    closed = Column(Boolean)
    sticky = Column(Boolean)

Base.metadata.create_all(engine)

