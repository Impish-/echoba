# -*- coding: utf-8 -*-
from wtforms import BooleanField, validators, PasswordField, SelectField, StringField, SubmitField, ValidationError, \
    HiddenField, IntegerField, RadioField
from wtforms.validators import InputRequired, EqualTo
from wtforms_alchemy import model_form_factory
from wtforms_tornado import Form
from manage.models import Staff, Board
from toolz.bd_toolz import with_session

ModelForm = model_form_factory(Form)


class StaffForm(Form):
    username = StringField(u'Юзернэйм', [validators.Length(min=4, max=25,
                                                           message=u'от 4 до 25 Символов!')])
    role = SelectField(u'Роль', choices=[('mod', 'Moderator'), ('adm', 'Admin')])


class StaffEditForm(StaffForm):
    password = PasswordField(u'Пароль', [EqualTo('confirm',
                                             message=u'Не совпадают ;(')
                                     ]
                         )
    confirm = PasswordField(u'Еще раз')

    id = HiddenField(label='')

    def validate_password(self, field):
        if field.data:
            if len(field.data) not in range(6,25):
                raise ValidationError(u'от 6 до 25 Символов!')


class StaffAddForm(StaffForm):
    password = PasswordField(u'Пароль', [validators.Length(min=6, max=25,
                                                        message=u'от 6 до 25 Символов!'),
                                     InputRequired(message=u'Обязательно!'),
                                     EqualTo('confirm',
                                             message=u'Не совпадают ;(')
                                     ]
                         )
    confirm = PasswordField(u'Еще раз')

    def validate_username(form, field):
        if Staff.get_user(username=field.data):
            raise ValidationError(u'Юзернэйм занят!')


class AddBoardForm(ModelForm):
    class Meta:
        model = Board

    @classmethod
    @with_session
    def get_session(cls,session):
        return session

    def save(self):
        kwargs = {}
        for key, field in self._fields.items():
            kwargs.update({key: self[key].data})
        obj = self.Meta.model(**kwargs)
        obj.save()
        return obj
