# -*- coding: utf-8 -*-
from torgen.detail import DetailHandler
from torgen.edit import FormMixin, FormHandler, BaseFormHandler
from tornado.web import RequestHandler

from manage.forms import StaffAddForm, StaffEditForm, AddBoardForm
from manage.models import Staff, Board
import tornado
from jinja2 import Environment, PackageLoader
from toolz.base_cls import BaseMixin, FlashMixin, BaseHandler
from toolz.bd_toolz import only_admin

env = Environment(loader=PackageLoader('manage', 'templates'))


class LogOutHandler(RequestHandler, BaseMixin):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        if self.get_current_user():
            self.clear_cookie("user_id")
        self.redirect('/manage')


class ManageHandler(BaseHandler):
    """
    Login
    """

    def get(self, *args, **kwargs):
        self.write(env.get_template('manage.html').render(self.get_context()))

    def post(self):
        user = Staff.get_auth(name=self.get_argument("login"), password=self.get_argument('password'))

        if user is None:
            return self.get()
        self.set_secure_cookie("user_id", '%d' % user.id)
        self.redirect("/manage")


class StaffManageHandler(BaseHandler, FlashMixin):
    template = 'staff.html'
    template_env = env
    form = StaffAddForm

    @only_admin
    # staff_list
    def get(self, *args, **kwargs):
        del_user = self.get_flash(key='del_user')
        self.render_template(del_message=del_user)

    @only_admin
    def post(self, *args, **kwargs):
        # staff_add
        form = self.get_form()
        if not form.validate():
            return self.render_template(form=form)

        staff = Staff()
        form.populate_obj(staff)
        staff.add()
        self.render_template()

    def get_context(self):
        context = super(self.__class__, self).get_context()
        context.update({
            'staff_list': Staff.get_users(),
        })
        return context


class DelStaffManagehandler(BaseHandler, FlashMixin):
    @only_admin
    def get(self, *args, **kwargs):
        username = kwargs.get('username', None)
        if self.current_user.name != username:
            Staff.remove_user(name=username)  # ;(
            self.set_flash(u'Юзверя ' + username + u' больше не существует', key='del_user')
        else:
            self.set_flash(u'Нельзя удалить самого себя', key='del_user')
        self.redirect('/manage/staff')


class EditStaffManageHandler(BaseMixin, DetailHandler, FormMixin):
    template_name = 'staff_edit.html'
    model = Staff
    context_object_name = 'user'
    form_class = StaffEditForm

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['form'] = self.form_class(obj=self.object)
        return context

    @only_admin
    def post(self, *args, **kwargs):
        self.kwargs = kwargs
        self.object = self.get_object()
        form = self.form_class(self.request.arguments)
        return self.form_valid(form) if form.validate() else self.form_invalid(form)

    def form_invalid(self, form):
        return self.render(self.get_context_data(message_form=form))

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
        return self.render(self.get_context_data())


class AddBoardHandler(BaseHandler):
    template_env = env
    template = 'add_board.html'
    form = AddBoardForm
    model = Board

    def get(self, *args, **kwargs):
        self.render_template(form=self.form())

    def post(self, *args, **kwargs):
        form = self.get_form()
        if form.validate():
            board = Board()
            form.populate_obj(board)
            board.add()
            return self.get()

        self.render_template(form=form)
