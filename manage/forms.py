# -*- coding: utf-8 -*-
import re
from sqlalchemy.orm import undefer_group, load_only
from wtforms import  validators, PasswordField, ValidationError, FileField, Form, BooleanField, StringField, HiddenField
from wtforms.validators import InputRequired, EqualTo

from manage.models import Staff, Board, Section, Message
from toolz.bd_toolz import with_session

from toolz.form_base import FormCBV
from toolz.recaptcha import RecaptchaValidator, RecaptchaField


class MessageEdit(FormCBV):
    class Meta:
        exclude = ['datetime', 'deleted']
        model = Message

    id = HiddenField('')
    captcha = RecaptchaField(validators=[RecaptchaValidator()])

    # image = FileField(u'Изображение')


class MessagesFilters(FormCBV):
    images_only = BooleanField(u'Только с картинкой',)
    poster_ip = StringField(u'IP отправителя')


class SectionForm(FormCBV):
    class Meta:
        model = Section


class AddBoardForm(FormCBV):
    class Meta:
        model = Board

    def validate_section_id(self, field):
        session = self.get_session()
        field.data = field.data if field.data > 0 else None
        if field.data is None:
            return
        if field.data not in [x.id for x in session.query(Section).options(load_only("id")).all()]:
            raise ValueError(u'Неверный раздел')

    def validate_available_from(self, field):
        time = re.match(r'(?P<hour>\d{1,2})\:(?P<min>\d{2})', field.data)
        if not time:
            raise ValidationError(u'Формат "ЧЧ:MM"')
        if int(time.group('hour')) not in range(0, 24):
            raise ValidationError(u'Неверное время! Формат "ЧЧ:ММ"')
        if int(time.group('min')) not in range(0, 60):
            raise ValidationError(u'Неверное время! Формат "ЧЧ:ММ"')

    def validate_available_until(self, field):
        time = re.match(r'(?P<hour>\d{1,2})\:(?P<min>\d{2})', field.data)
        if not time:
            raise ValidationError(u'Формат "ЧЧ:MM"')
        if int(time.group('hour')) not in range(0, 24):
            raise ValidationError(u'Неверное время! Формат "ЧЧ:ММ"')
        if int(time.group('min')) not in range(0, 60):
            raise ValidationError(u'Неверное время! Формат "ЧЧ:ММ"')


class EditBoardForm(AddBoardForm):
    def process(self, formdata=None, obj=None, data=None, **kwargs):
        self.dir.validators = []
        self.name.validators = []
        super(EditBoardForm, self).process(formdata=formdata, obj=obj, data=data, **kwargs)

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


class StaffForm(FormCBV):
    class Meta:
        model = Staff


class StaffEditForm(StaffForm):
    class Meta:
        exclude = ['password',]

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
        try:
            self.boards.set_object(obj)
        except AttributeError:
            pass
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
