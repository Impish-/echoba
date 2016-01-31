# -*- coding: utf-8 -*-
import shutil

import tornado
from sqlalchemy_imageattach.context import store_context
from torgen.base import TemplateHandler
from torgen.detail import DetailHandler
from torgen.edit import DeleteHandler
from torgen.list import ListHandler
from tornado.web import RequestHandler

from manage.dynamic_form_fields import StaffDynamicForm, BoardDynamicForm, FilterDynamicForm
from manage.forms import StaffAddForm, StaffEditForm, AddBoardForm, EditBoardForm, SectionForm, MessageEdit, \
    MessagesFilters
from manage.models import Staff, Board, Message, BoardImage, Section
from settings import store
from toolz.base_cls import FlashMixin, FormMixinReversed, BoardDataMixin, SuccessReverseMixin, FormMixin
from toolz.decorators.check_rights import admin_only, can_moderate, login_required


class ManageHandler(BoardDataMixin, TemplateHandler):
    template_name = 'manage.html'

    def post(self):
        user = self.db.query(Staff).filter(Staff.name == self.get_argument("login"),
                                           Staff.active == True).first()
        try:
            if not user.password == self.get_argument('password', None):
                return self.get()
        except AttributeError:
            return self.get()
        self.set_secure_cookie("user_id", '%d' % user.id)
        self.redirect("/manage")


@login_required
class LogOutHandler(BoardDataMixin, TemplateHandler):
    template_name = 'manage.html'

    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        if self.get_current_user():
            self.clear_cookie("user_id")
        self.redirect('/manage')


@admin_only
class StaffManageHandler(BoardDataMixin, StaffDynamicForm, ListHandler, FormMixinReversed):
    template_name = 'staff.html'
    form_class = StaffAddForm
    model = Staff
    context_object_name = 'staff_list'
    success_url_reverse_args = ['staff_list']


@admin_only
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


@admin_only
class DelStaffManageHandler(BoardDataMixin, SuccessReverseMixin, DeleteHandler, FlashMixin):
    template_name = 'confirm_delete.html'
    model = Staff
    success_url_reverse_args = ['staff_list']


@login_required
@can_moderate
class DelMessageManageHandler(BoardDataMixin, DeleteHandler, FlashMixin):
    template_name = 'confirm_delete.html'
    model = Message
    success_url = '/manage/'
    slug_url_kwarg = 'gid'  # defaults to slug
    slug_field = Message.gid

    def get_object(self):
        obj = self.db.query(Message).filter(Message.gid == self.kwargs.get(self.slug_url_kwarg, None)).first()
        return obj

    def post(self, *args, **kwargs):
        with store_context(store):
            message = self.db.query(Message).filter(Message.gid == kwargs.get('gid', 0)).first()
            if message is None:
                pass

            if message and message.id == message.thread.op().id:
                message.thread.deleted = True
                messages = self.db.query(Message).filter(Message.thread_id == message.thread_id).all()
                for mess in messages:
                    mess.deleted = True
                    if mess.picture:
                        try:
                            shutil.rmtree('%simages/%s' % (store.path, str(mess.id)))
                        except:
                            pass  # Ну нет, так нет
                        self.db.query(BoardImage).filter(BoardImage.message_gid == mess.id).delete()
            else:
                message.deleted = True
                if message.picture:
                    try:
                        shutil.rmtree('%simages/%s' % (store.path, str(message.id)))
                    except:
                        pass  # Что тут поделаешь...
                    self.db.query(BoardImage).filter(BoardImage.message_id == message.id).delete()
            self.db.commit()
            self.redirect(self.success_url)


@login_required
@can_moderate
class EditMessageHandler(BoardDataMixin, FormMixinReversed, DetailHandler):
    template_name = 'edit_message.html'
    model = Message
    form_class = MessageEdit
    slug_url_kwarg = 'gid'  # defaults to slug
    slug_field = Message.gid
    success_url_reverse_args = ['edit_message', 'gid']

    def get_object(self):
        obj = self.db.query(Message).filter(Message.gid == self.kwargs.get(self.slug_url_kwarg, None)).first()
        if not self.get_current_user().is_admin:
            if not obj.board.id in [x.id for x in self.get_current_user().boards]:
                raise self.send_error(status_code=403)
        return obj


@login_required
class MessageListHandler(BoardDataMixin, FilterDynamicForm, ListHandler, FormMixin):
    template_name = 'messages_list.html'
    model = Message
    paginate_by = 30
    context_object_name = 'messages_list'
    form_class = MessagesFilters

    def post(self, *args, **kwargs):
        self.send_error(status_code=403)

    def get_queryset(self):
        query = self.db.query(self.model)
        user = self.get_current_user()
        if not user.all_boards and not user.is_admin():
            query = query.filter(Message.board_id.in_([x.id for x in self.get_current_user().boards]))
        if user.is_admin():
            all_boards = self.db.query(Board).all()
            query = query.filter(Message.board_id.in_([x.id for x in all_boards]))
        query = query.join(BoardImage, BoardImage.message_gid == Message.gid) if self.get_argument('images_only', None) \
            else query
        ip_filter = self.get_argument('poster_ip', None)
        if ip_filter:
            query = query.filter(Message.ip_address == ip_filter)
        filtred_board = self.get_argument('boards', 0)
        if int(filtred_board) > 0:
            query = query.filter(Message.board_id == filtred_board)
        return query.order_by(Message.gid.desc())


@admin_only
class SectionHandler(BoardDataMixin, ListHandler, FormMixinReversed):
    template_name = 'section.html'
    form_class = SectionForm
    model = Section
    paginate_by = 30
    context_object_name = 'section_list'
    success_url_reverse_args = ['section_list']


@admin_only
class EditSectionHandler(BoardDataMixin, FormMixinReversed, DetailHandler):
    template_name = 'section.html'
    form_class = SectionForm
    model = Section
    success_url_reverse_args = ['section_list']


@admin_only
class DelSectionHandler(BoardDataMixin, SuccessReverseMixin, DeleteHandler, FlashMixin):
    template_name = 'confirm_delete.html'
    model = Section
    success_url_reverse_args = ['section_list']


@login_required
class AddBoardHandler(BoardDataMixin, BoardDynamicForm, FormMixinReversed, TemplateHandler):
    template_name = 'add_board.html'
    form_class = AddBoardForm
    model = Board
    # success_url_reverse_args = ['board_edit', 'id']
    success_url_reverse_args = ['manage']

    def form_valid(self, form):
        super(AddBoardHandler, self).form_valid(form)
        if not self.get_current_user().is_admin():
            board = self.get_object()
            board.staff.add(self.get_current_user())
            self.db.commit()


@login_required
@can_moderate
class EditBoardHandler(BoardDataMixin, BoardDynamicForm, FormMixinReversed, DetailHandler):
    template_name = 'board_edit.html'
    model = Board
    context_object_name = 'user'
    form_class = EditBoardForm
    success_url_reverse_args = ['board_edit', 'id']


@login_required
@can_moderate
class DeleteBoardHandler(BoardDataMixin, SuccessReverseMixin, DeleteHandler, FlashMixin):
    template_name = 'confirm_delete.html'
    model = Board
    success_url_reverse_args = ['manage']
