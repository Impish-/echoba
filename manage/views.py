# -*- coding: utf-8 -*-
from torgen.base import TemplateHandler
from torgen.detail import DetailHandler
from torgen.edit import FormHandler, DeleteHandler
from torgen.list import ListHandler
from tornado.web import RequestHandler

from manage.forms import StaffAddForm, StaffEditForm, AddBoardForm
from manage.models import Staff, Board
import tornado
from jinja2 import Environment, PackageLoader
from toolz.base_cls import BaseMixin, FlashMixin, FormMixin
from toolz.bd_toolz import only_admin

env = Environment(loader=PackageLoader('manage', 'templates'))


class ManageHandler(BaseMixin, TemplateHandler):
    template_name = 'manage.html'

    def post(self):
        user = self.db.query(Staff).filter(Staff.name == self.get_argument("login"),
                                           Staff.password == self.get_argument('password')).first()
        if user is None:
            return self.get()
        self.set_secure_cookie("user_id", '%d' % user.id)
        self.redirect("/manage")


class LogOutHandler(BaseMixin, tornado.web.RequestHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        if self.get_current_user():
            self.clear_cookie("user_id")
        self.redirect('/manage')


class StaffManageHandler(BaseMixin, ListHandler, FormMixin):
    template_name = 'staff.html'
    form_class = StaffAddForm
    model = Staff
    context_object_name = 'staff_list'

    def form_invalid(self, form):
        self.object_list = self.get_queryset()
        context_form = self.get_context_data(**self.kwargs)
        context_form['form'] = form
        return super(ListHandler, self).render(context_form)

    def form_valid(self, form):
        staff = Staff()
        form.populate_obj(staff)
        staff.add()
        return super(self.__class__, self).form_valid(form)


class EditStaffManageHandler(BaseMixin, DetailHandler, FormMixin):
    template_name = 'staff_edit.html'
    model = Staff
    context_object_name = 'user'
    form_class = StaffEditForm

    def form_invalid(self, form):
        context_form = super(self.__class__, self).get_context_data(**self.kwargs)
        context_form['form'] = form
        return self.render(context_form)

    def form_valid(self, form):
        user = self.object
        user.name = form.name.data if form.name.data else user.name
        user.password = form.password.data if form.password.data else user.password
        user.role = form.role.data if form.role.data else user.role.name
        user.all_boards = form.all_boards.data
        user.boards[:] = []
        for b_id in form.boards.data:
            if b_id not in [x.id for x in user.boards]:
                user.boards.append(self.db.query(Board).get(b_id))
        self.db.commit()
        self.db.refresh(user)
        return super(self.__class__, self).form_valid(form)


class DelStaffManageHandler(BaseMixin, DeleteHandler, FlashMixin):
    template_name = 'confirm_delete.html'
    model = Staff
    success_url = '/manage/staff'


class AddBoardHandler(BaseMixin, FormHandler):
    template_name = 'add_board.html'
    form_class = AddBoardForm
    model = Board
    success_url = '/manage'

    def get_success_url(self):
        return self.redirect(self.success_url)

    def post(self, *args, **kwargs):
        self.kwargs = kwargs
        form = self.form_class(self.request.arguments)
        return self.form_valid(form) if form.validate() else self.form_invalid(form)

    def form_invalid(self, form):
        context_form = self.get_context_data()
        context_form['form'] = form
        return self.render(context_form)

    def form_valid(self, form):
        board = self.model()
        form.populate_obj(board)
        self.db.add(board)
        self.db.commit()
        return self.get_success_url()
