#encoding: utf-8
from wtforms import validators
from wtforms import SelectField

from manage.models import Section, Board
from toolz.fields import MultiCheckboxField


class BoardDynamicForm:
    def get_form(self, form_class):
        sections = self.db.query(Section).all()
        self.form_class.append_field('section_id',
                                     SelectField(u'Раздел',
                                                 choices=[(0, u'<Не выбрано>')]+[(x.id, x.name) for x in sections],
                                                 default=0, coerce=int))
        return self.form_class(**self.get_form_kwargs())


class StaffDynamicForm:
    def get_form(self, form_class):
        boards = self.db.query(Board).all()
        self.form_class.append_field('boards',
                                     MultiCheckboxField(u'Модерируемые доски', choices=
                        [(x.id, x.name) for x in boards], validators=[validators.Optional()], coerce=int))
        return self.form_class(**self.get_form_kwargs())