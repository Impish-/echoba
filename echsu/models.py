# -*- coding: utf-8 -*-

from sqlalchemy import String, Integer, ForeignKey, BOOLEAN, Table, UnicodeText
from sqlalchemy_defaults import Column
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship, backref
from sqlalchemy_imageattach.entity import image_attachment, Image
from sqlalchemy_utils import PasswordType, ChoiceType, IPAddressType, URLType

from manage.models import Board
from toolz.base_models import SessionMixin
from toolz.bd_toolz import with_session, engine

Base = declarative_base()

#
#TODO: video
# class Video():
#    url =
#   hosting =

# def get_driver() - сценарий работы с хостингом
#


class Message(Base, SessionMixin):
    poster_name = Column(String, label=u'Имя')
    email = Column(String, label=u'E-Mail')
    header = Column(String, label=u'Заголовок')
    message = Column(UnicodeText, label=u'Сообщение')
    picture = image_attachment('BoardPicture')
    password = Column(PasswordType, label=u'Пароль(для удаления поста)')
    #
    #mod_hash = Хэшкод модератора
    #mad_action = список действий модератора(подписаться,создать прикрепленный/закрытый тред, row_html, другая еба)
    ip_address = Column(IPAddressType)


class BoardPicture(Base, Image, SessionMixin):
    message_id = Column(Integer, ForeignKey('message.id'), primary_key=True)
    message = relationship('Message')


class Thread(Base, SessionMixin):
    name = Column(String, label=u'Название')
    sticky = Column(BOOLEAN, label=u'Прикреплен')
    closed = Column(BOOLEAN, label=u'Закрыт')
    board = relationship(Board)
    messages = relationship("Message", backref=backref('message', lazy='dynamic',),)



