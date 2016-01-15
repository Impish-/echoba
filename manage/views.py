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


class StaffManageHandler(BaseHandler):
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


# TODO: ябануть get_object()
class EditStaffManageHandler(BaseHandler):
    template = 'staff_edit.html'
    template_env = env
    form = StaffEditForm
    model = Staff

    def put(self, *args, **kwargs):
        print 'put'

    @only_admin
    def get(self, *args, **kwargs):
        self.username = kwargs.get('username', None)
        self.render_template(user=self.get_user()) if self.get_user() else self.write('Нету')

    def get_user(self):
        return Staff.get_user(self.username)

    @only_admin
    def post(self, *args, **kwargs):
        self.username = kwargs.get('username', None)
        user = Staff.get_user(self.username)
        form = self.get_form()
        if form.validate():
            for b_id in form.boards.data:
                user.add_mod_rights(b_id)
            user.save()
            user = Staff.update_user(id=form.id.data,
                                     name=form.name.data,
                                     password=form.password.data,
                                     role=form.role.data,)


            self.username = user.name
            self.render_template(user=user)
        self.render_template(user=user, form=form)

    def get_context(self, **kwargs):
        context = super(self.__class__, self).get_context()
        user = self.get_user()
        context.update({
            'form': StaffEditForm(obj=user),
        })
        return context


# TODO: Примерно на такой вид вьюшек(аля-жанго) перевести все
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
