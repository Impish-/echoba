# -*- coding: utf-8 -*-

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy_utils import PasswordType, ChoiceType


from toolz.base_models import SessionMixin
from toolz.bd_toolz import with_session, engine

Base = declarative_base()


class ModRights(Base):
    __tablename__ = 'mod_rights'
    moder = Column(Integer, ForeignKey('staff.id'), primary_key=True)
    board = Column(Integer, ForeignKey('board.id'), primary_key=True)
    extra_data = Column(String(50))
    staff = relationship("Staff", back_populates="boards")
    boards = relationship("Board", back_populates="staff")


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
    boards = relationship("ModRights", back_populates="staff")

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
    def get_auth(username, password, session=None):
        user = session.query(Staff).filter(Staff.name == username).first()
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
    def get_user(username, session):
        return session.query(Staff).filter(Staff.name == username).first()

    @staticmethod
    @with_session
    def get_user_by_id(id, session):
        return session.query(Staff).filter(Staff.id == id).first()

    @staticmethod
    @with_session
    def remove_user(name, session):
        session.query(Staff).filter(Staff.name == name).delete(synchronize_session=False)
        session.commit()

    @staticmethod
    @with_session
    def get_users(session):
        return session.query(Staff).all()


class Board(Base, SessionMixin):
    name = Column(String, unique=True)
    dir = Column(String, unique=True)
    threads_on_page = Column(Integer, default=9)
    default_name = Column(String, default='Anonymouse')
    max_pages = Column(Integer, default=11)
    staff = relationship("ModRights", back_populates="boards")

    def __init__(self, name, dir):
        self.name = name
        self.dir = dir

    def __repr__(self):
        return "<User('%s', '%s')>" % (self.name, self.dir)

Base.metadata.create_all(engine)

