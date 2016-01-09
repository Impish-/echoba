from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declared_attr

from toolz.bd_toolz import with_session


class SessionMixin:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)

    @declared_attr
    @with_session
    def session(self, session):
        return session

    #!!]eqyz
    @with_session
    def save(self, session):
        session.add(self)
        session.commit()
        return self