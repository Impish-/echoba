# -*- coding: utf-8 -*-
from wtforms import BooleanField, validators, PasswordField, SelectField, StringField, SubmitField, ValidationError, \
    HiddenField, IntegerField, RadioField, SelectMultipleField, widgets, SelectMultipleField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms.validators import InputRequired, EqualTo
from wtforms.widgets import HTMLString, html_params
from wtforms_alchemy import model_form_factory, ModelFormField

from wtforms_tornado import Form
from manage.models import Staff, Board
from toolz.bd_toolz import with_session
from wtforms.compat import text_type

ModelForm = model_form_factory(Form)


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

    def set_object(self, obj):
        self.obj = obj

    def iter_choices(self):
        for value, label in self.choices:
            boards = []
            try:
                boards = self.obj.boards
            except AttributeError:
                pass
            selected = self.coerce(value) in [x.id for x in boards]
            yield (value, label, selected)


# Эталон формы!
class AddBoardForm(ModelForm):
    class Meta:
        model = Board



class StaffForm(ModelForm):
    class Meta:
        model = Staff

    # @classmethod
    # @with_session
    # def get_session(cls, session):
    #     return session


class StaffEditForm(StaffForm):
    class Meta:
        exclude = ['password', 'name']

    boards = MultiCheckboxField(u'Модерируемые доски', choices=
                        [(x.id, x.name) for x in Board.get_all()], validators=[validators.Optional()], coerce=int)

    name = StringField(u'Юзернэйм', [validators.Length(min=4, max=25,
                                                           message=u'от 4 до 25 Символов!')])

    password = PasswordField(u'Пароль', [EqualTo('confirm', message=u'Не совпадают ;(')])
    confirm = PasswordField(u'Еще раз')

    def validate_password(self, field):
        if field.data:
            if len(field.data) not in range(6, 25):
                raise ValidationError(u'от 6 до 25 Символов!')

    def process(self, formdata=None, obj=None, data=None, **kwargs):
        #TODO: подумать как иначе
        self.boards.set_object(obj)
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
