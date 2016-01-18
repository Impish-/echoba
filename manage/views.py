# -*- coding: utf-8 -*-
from torgen.base import TemplateHandler
from torgen.detail import DetailHandler
from torgen.edit import FormHandler, DeleteHandler, ProcessFormHandler
from torgen.list import ListHandler
from tornado.web import RequestHandler

from manage.forms import StaffAddForm, StaffEditForm, AddBoardForm, EditBoardForm
from manage.models import Staff, Board, Message, Thread, BoardImage
import tornado
from jinja2 import Environment, PackageLoader
from toolz.base_cls import BaseMixin, FlashMixin, FormMixin, BoardDataMixin
from toolz.bd_toolz import only_admin
from sqlalchemy_imageattach.context import store_context
from settings import store

import shutil


class ManageHandler(BoardDataMixin, TemplateHandler):
    template_name = 'manage.html'

    def post(self):
        user = self.db.query(Staff).filter(Staff.name == self.get_argument("login")).first()
        if user.password == self.get_argument('password', None) is None:
            return self.get()
        self.set_secure_cookie("user_id", '%d' % user.id)
        self.redirect("/manage")


class LogOutHandler(BoardDataMixin, TemplateHandler):
    template_name = 'manage.html'

    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        if self.get_current_user():
            self.clear_cookie("user_id")
        self.redirect('/manage')


class StaffManageHandler(BoardDataMixin, ListHandler, FormMixin):
    template_name = 'staff.html'
    form_class = StaffAddForm
    model = Staff
    context_object_name = 'staff_list'

    def post(self, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super(self.__class__,self).post(args, kwargs)

    def get_success_url(self):
        return self.reverse_url('staff_list')


class EditStaffManageHandler(BoardDataMixin, DetailHandler, FormMixin):
    template_name = 'staff_edit.html'
    model = Staff
    context_object_name = 'user'
    form_class = StaffEditForm

    def get_success_url(self):
        return self.redirect(self.reverse_url('edit_staff', self.object.id))

    def form_valid(self, form):
        user = self.object
        user.all_boards = form.all_boards.data
        user.boards[:] = []
        for b_id in form.boards.data:
            if b_id not in [x.id for x in user.boards]:
                user.boards.append(self.db.query(Board).get(b_id))
        form._fields.pop('boards')
        form.populate_obj(user)
        self.db.commit()
        self.db.refresh(user)
        return self.redirect(self.get_success_url())


class DelStaffManageHandler(BoardDataMixin, DeleteHandler, FlashMixin):
    template_name = 'confirm_delete.html'
    model = Staff
    success_url = '/manage/staff'


class DelMessageManageHandler(BoardDataMixin, DeleteHandler, FlashMixin):
    template_name = 'confirm_delete.html'
    model = Message
    success_url = '/manage/'

    def post(self, *args, **kwargs):
        with store_context(store):
            message = self.db.query(Message).filter(Message.id==kwargs.get('id', 0)).first()
            if message and message.id == message.thread.op().id:
                message.thread.deleted = True
                messages = self.db.query(Message).filter(Message.thread_id==message.thread_id).all()
                for mess in messages:
                    mess.deleted = True
                    if mess.picture:
                        try:
                            shutil.rmtree('%simages/%s' % (store.path, str(mess.id)))
                        except:
                            pass # Ну нет, так нет
                        self.db.query(BoardImage).filter(BoardImage.message_id==mess.id).delete()
            else:
                message.deleted = True
                if message.picture:
                    try:
                        shutil.rmtree('%simages/%s' % (store.path, str(message.id)))
                    except:
                        pass # Что тут поделаешь...
                    self.db.query(BoardImage).filter(BoardImage.message_id==message.id).delete()
            self.db.commit()
            self.redirect(self.success_url)


class AddBoardHandler(BoardDataMixin, FormMixin, TemplateHandler):
    template_name = 'add_board.html'
    form_class = AddBoardForm
    model = Board
    success_url = '/manage'

    def get_success_url(self):
        return self.redirect(self.success_url)


class EditBoardHandler(BoardDataMixin, DetailHandler, FormMixin):
    template_name = 'board_edit.html'
    model = Board
    context_object_name = 'user'
    form_class = EditBoardForm

    def get_success_url(self):
        return self.redirect(self.reverse_url('board_edit', self.object.id))
