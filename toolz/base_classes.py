# encoding: utf-8
import tornado
from ming import create_datastore, Session
from ming.odm import MappedClass, ThreadLocalODMSession

from settings import USER_CLASS
bind = create_datastore('board')


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        try:
            return USER_CLASS.get_user_by_name(tornado.escape.json_decode(self.get_secure_cookie("user")))
        except:
            return None


class BaseMappedClass(MappedClass):

    class __mongometa__:
        pass

    def __init__(self):
        self.doc_session = Session(bind)
        self.session = ThreadLocalODMSession(doc_session=self.doc_session)
        self.__mongometa__.session = self.session

    def update_kwargs(self, obj, **kwargs):
        """
        Новые значения для всех не списковых полей класса
        """
        for key, value in kwargs.items():
            if key in dir(obj):
                obj[key] = value
        return obj

    @staticmethod
    def save():
        BaseMappedClass.session.flush()
        BaseMappedClass.session.clear()