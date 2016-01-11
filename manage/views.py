# -*- coding: utf-8 -*-
from manage.forms import StaffAddForm, StaffEditForm, AddBoardForm
from manage.models import Staff, Board
import tornado
from jinja2 import Environment, PackageLoader
from toolz.base_cls import BaseHandler
from toolz.bd_toolz import only_admin

env = Environment(loader=PackageLoader('manage', 'templates'))


class LogOutHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        if self.get_current_user():
            self.clear_cookie("user_id")
        self.redirect('/manage')


class ManageHandler(BaseHandler):
    def get(self, *args, **kwargs):
        self.write(env.get_template('manage.html').render(self.get_context()))

    def post(self):
        user = Staff.get_auth(name=self.get_argument("login"), password=self.get_argument('password'))

        if user is None:
            return self.get()
        self.set_secure_cookie("user_id", '%d' % user.id)
        self.redirect("/manage")


class StaffManageHandler(BaseHandler):
    template = 'staff.html'
    template_env = env

    @only_admin
    # staff_list
    def get(self, *args, **kwargs):
        del_user = self.get_flash(key='del_user')
        self.render_template(del_message=del_user)

    @only_admin
    def post(self, *args, **kwargs):
        # staff_add
        #TODO: переделать на modelform
        form = StaffAddForm(self.request.arguments)
        if form.validate():
            Staff.create_user(name=form.username.data,
                              password=form.password.data,
                              role=form.role.data)
            self.render_template()
            return
        self.render_template(form=form)

    def get_context(self):
        context = super(self.__class__, self).get_context()
        context.update({
            'staff_list': Staff.get_users(),
            'form': StaffAddForm(),
        })
        return context


class DelStaffManagehandler(BaseHandler):
    @only_admin
    def get(self, *args, **kwargs):
        username = kwargs.get('username', None)
        if self.current_user.name != username:
            Staff.remove_user(name=username)  # ;(
            self.set_flash(u'Юзверя ' + username + u' больше не существует', key='del_user')
        else:
            self.set_flash(u'Нельзя удалить самого себя', key='del_user')
        self.redirect('/manage/staff')


class EditStaffManageHandler(BaseHandler):
    template = 'staff_edit.html'
    template_env = env

    @only_admin
    def get(self, *args, **kwargs):
        self.username = kwargs.get('username', None)
        self.render_template(user=self.get_user())

    def get_user(self):
        return Staff.get_user(self.username)

    @only_admin
    def post(self, *args, **kwargs):
        user = Staff.get_user(kwargs.get('username', None))
        form = StaffEditForm(self.request.arguments)

        if form.validate():
            user = Staff.update_user(name=form.username.data,
                                     password=form.password.data,
                                     role=form.role.data,
                                     id=form.id.data)
            return self.get(username=user.name)
        self.username = kwargs.get('username', None)
        self.render_template(form=form, user=user)

    def get_context(self):
        context = super(self.__class__, self).get_context()
        user = self.get_user()
        context.update({
            'form': StaffEditForm(username=user.name,
                                  role=user.role.code,
                                  id=user.id),
        })
        return context




# TODO: Примерно на такой вид вьюшек(аля-жанго) перевести все
class AddBoardHandler(BaseHandler):
    template_env = env
    template = 'add_board.html'
    form = AddBoardForm

    def get(self, *args, **kwargs):
        self.render_template(form=self.form())

    def post(self, *args, **kwargs):
        form = self.form(self.request.arguments)
        if form.validate():
            board = form.save()
            return self.get()

        self.render_template(form=form)
