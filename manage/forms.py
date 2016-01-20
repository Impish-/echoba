# -*- coding: utf-8 -*-
from sqlalchemy.orm import undefer_group, load_only
from wtforms import BooleanField, validators, PasswordField, SelectField, StringField, SubmitField, ValidationError, \
    HiddenField, IntegerField, RadioField, SelectMultipleField, widgets, SelectMultipleField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms.validators import InputRequired, EqualTo
from wtforms.widgets import HTMLString, html_params
from wtforms_alchemy import model_form_factory, ModelFormField

from wtforms_tornado import Form
from manage.models import Staff, Board, Section
from toolz.bd_toolz import with_session
from wtforms.compat import text_type

from toolz.fields import MultiCheckboxField

ModelForm = model_form_factory(Form)


class SectionForm(ModelForm):
    class Meta:
        model = Section

    @classmethod
    @with_session
    def get_session(cls, session):
        return session


class AddBoardForm(ModelForm):
    class Meta:
        model = Board

    section_id = SelectField(u'Раздел', choices=[(0, u'<Не выбрано>')]+[(x.id, x.name) for x in Section.get_all()],
                             default=0, coerce=int)

    def validate_section_id(self, field):
        session = self.get_session()
        if field.data not in [x.id for x in session.query(Section).options(load_only("id")).all()]:
            raise ValueError(u'Неверный раздел')

    @classmethod
    @with_session
    def get_session(cls, session):
        return session


class EditBoardForm(AddBoardForm):
    def process(self, formdata=None, obj=None, data=None, **kwargs):
        self.dir.validators = []
        self.name.validators = []
        super(self.__class__, self).process(formdata=formdata, obj=obj, data=data, **kwargs)

    def validate_name(self, field):
        session = self.get_session()
        try_get_board = session.query(Staff).filter(Board.name == field.data, Board.id != self._obj.id).first()
        if try_get_board:
            raise ValidationError(u'Занято другой доской')

    def validate_dir(self, field):
        session = self.get_session()
        try_get_board = session.query(Staff).filter(Board.dir == field.data, Board.id != self._obj.id).first()
        if try_get_board:
            raise ValidationError(u'Занято другой доской')


class StaffForm(ModelForm):
    class Meta:
        model = Staff

    @classmethod
    @with_session
    def get_session(cls, session):
        return session


class StaffEditForm(StaffForm):
    class Meta:
        exclude = ['password',]

    boards = MultiCheckboxField(u'Модерируемые доски', choices=
                        [(x.id, x.name) for x in Board.get_all()], validators=[validators.Optional()], coerce=int)

    password = PasswordField(u'Пароль', [EqualTo('confirm', message=u'Не совпадают ;(')])
    confirm = PasswordField(u'Еще раз')

    def validate_password(self, field):
        if field.data:
            if len(field.data) not in range(6, 25):
                raise ValidationError(u'от 6 до 25 Символов!')

    def validate_name(self, field):
        session = self.get_session()
        try_get_staff = session.query(Staff).filter(Staff.name == field.data, Staff.id != self._obj.id).first()
        if try_get_staff:
            raise ValidationError(u'Занято кем-то другим!')

    def process(self, formdata=None, obj=None, data=None, **kwargs):
        #TODO: подумать как иначе
        self.boards.set_object(obj)
        self.name.validators = []
        super(self.__class__, self).process(formdata=formdata, obj=obj, data=data, **kwargs)


class StaffAddForm(StaffForm):
    password = PasswordField(u'Пароль',
                             [validators.Length(min=6, max=25, message=u'от 6 до 25 Символов!'),
                              InputRequired(message=u'Обязательно!'),
                              EqualTo('confirm',
                                      message=u'Не совпадают ;(')
                              ]
                             )
    confirm = PasswordField(u'Еще раз')
