# -*- coding: utf-8 -*-
import shutil

import tornado
from sqlalchemy_imageattach.context import store_context
from torgen.base import TemplateHandler
from torgen.detail import DetailHandler
from torgen.edit import DeleteHandler
from torgen.list import ListHandler
from tornado.web import RequestHandler

from manage.dynamic_form_fields import StaffDynamicForm, BoardDynamicForm
from manage.forms import StaffAddForm, StaffEditForm, AddBoardForm, EditBoardForm, SectionForm
from manage.models import Staff, Board, Message, BoardImage, Section
from settings import store
from toolz.base_cls import FlashMixin, FormMixinReversed, BoardDataMixin, SuccessReverseMixin


class ManageHandler(BoardDataMixin, TemplateHandler):
    template_name = 'manage.html'

    def post(self):
        user = self.db.query(Staff).filter(Staff.name == self.get_argument("login")).first()
        print user.password == self.get_argument('password', None)
        try:
            if not user.password == self.get_argument('password', None):
                return self.get()
        except AttributeError:
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


class StaffManageHandler(BoardDataMixin, StaffDynamicForm, ListHandler, FormMixinReversed):
    template_name = 'staff.html'
    form_class = StaffAddForm
    model = Staff
    context_object_name = 'staff_list'
    success_url_reverse_args = ['staff_list']


class EditStaffManageHandler(BoardDataMixin, StaffDynamicForm, DetailHandler, FormMixinReversed):
    template_name = 'staff_edit.html'
    model = Staff
    context_object_name = 'user'
    form_class = StaffEditForm
    success_url_reverse_args = ['edit_staff', 'id']

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


class DelStaffManageHandler(BoardDataMixin, SuccessReverseMixin, DeleteHandler, FlashMixin):
    template_name = 'confirm_delete.html'
    model = Staff
    success_url_reverse_args = ['staff_list']


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


class MessageListHandler(BoardDataMixin, ListHandler):
    template_name = 'messages_list.html'
    model = Message
    paginate_by = 30
    context_object_name = 'messages_list'

    def get_queryset(self):
        #Потом Фильтры запилить
        # if self.get_current_user().all_boards:
        return self.db.query(self.model).order_by(Message.id.desc()).all()


class SectionHandler(BoardDataMixin, ListHandler, FormMixinReversed):
    template_name = 'section.html'
    form_class = SectionForm
    model = Section
    paginate_by = 30
    context_object_name = 'section_list'
    success_url_reverse_args = ['section_list']


class EditSectionHandler(BoardDataMixin, FormMixinReversed, DetailHandler):
    template_name = 'section.html'
    form_class = SectionForm
    model = Section
    success_url_reverse_args = ['section_list']


class DelSectionHandler(BoardDataMixin, SuccessReverseMixin, DeleteHandler, FlashMixin):
    template_name = 'confirm_delete.html'
    model = Section
    success_url_reverse_args = ['section_list']


class AddBoardHandler(BoardDataMixin, BoardDynamicForm, FormMixinReversed, TemplateHandler):
    template_name = 'add_board.html'
    form_class = AddBoardForm
    model = Board
    success_url_reverse_args = ['board_edit', 'id']


class EditBoardHandler(BoardDataMixin, BoardDynamicForm, FormMixinReversed, DetailHandler):
    template_name = 'board_edit.html'
    model = Board
    context_object_name = 'user'
    form_class = EditBoardForm
    success_url_reverse_args = ['board_edit', 'id']