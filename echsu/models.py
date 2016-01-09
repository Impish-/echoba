#encoding: utf-8
import hashlib
from bson import ObjectId
import datetime
import time
from ming import create_datastore
from ming import Session
from ming import schema
from ming.odm import ForeignIdProperty, RelationProperty, ThreadLocalODMSession, FieldProperty
from ming.odm import Mapper
from ming.odm.declarative import MappedClass

from manage.models import Board
from settings import password_salt

bind = create_datastore('board')
doc_session = Session(bind)
session = ThreadLocalODMSession(doc_session=doc_session)

#тут под монго, но таки все на PostgreSQL думаю сделать

# class Thread(MappedClass):
#     class __mongometa__:
#         session = session
#         name = 'thread'
#
#     _id = FieldProperty(schema.ObjectId)
#     op_id = FieldProperty(int)
#     bump_timestamp = FieldProperty(int)
#     bump_limited = FieldProperty(bool)
#     closed = FieldProperty(bool)
#     sticky = FieldProperty(bool)
#     title = FieldProperty(str)
#     messages = ForeignIdProperty('Message', uselist=True)
#
#
#     @staticmethod
#     def get_thread(op_id):
#         return Thread.query.get(op_id=op_id)
#
#     @staticmethod
#     def get_by_id(id):
#         return Thread.query.get(_id=ObjectId(id))
#
#     @staticmethod
#     def get_for_board(dir):
#         board = Board.Api.get_board(dir)
#         if board is None:
#             return []
#         return Thread.query.find({'board': ObjectId(board._id)}).all()
#
#     def get_messages(self, op_id, tail):
#         return [Message.query.get(_id=ObjectId(message)) for message in self.get_thread(op_id).messages]
#
#
# class Message(MappedClass):
#     class __mongometa__:
#         session = session
#         name = 'message'
#
#     _id = FieldProperty(schema.ObjectId)
#     date = FieldProperty(str)
#     num = FieldProperty(int)
#     message = FieldProperty(str)
#     password = FieldProperty(str)
#     poster_name = FieldProperty(str)
#     email = FieldProperty(str)
#     file = FieldProperty(str)
#     image_thumb = FieldProperty(str)
#
#
#     @staticmethod
#     def get_message(num):
#         return Message.query.get(num=num)
#
#     def add_message(self, **kwargs):
#         print self.request.files
#         board = Board.Api.get_board(kwargs.get('board', [None])[0])
#         board.post_count += 1
#
#         now = datetime.datetime.now()
#
#         kwargs.update({
#             'num': [board.post_count],
#             'board': [board._id],
#             'date': [now.strftime("%d. %B %Y %I:%M (%A)")],
#             'bump_timestamp': [int(time.mktime(now.timetuple()))]
#         })
#
#         message = self.update_kwargs(Message(), **kwargs)
#         try:
#             thread = Thread.Api.get_thread(int(kwargs.get('reply_thread', [None])[0]))
#             thread.messages.append(message._id)
#
#         except:
#             thread = self.update_kwargs(Thread(), **kwargs)
#             thread.op_id = message.num
#         finally:
#             thread.save()

Mapper.compile_all()