from wtforms import SelectMultipleField

from wtforms import widgets
from wtforms.utils import unset_value

from toolz.widgets import DivWidget


class MultiCheckboxField(SelectMultipleField):
    widget = DivWidget()
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
            print self.__class__.__dict__
            selected = self.coerce(value) in [x.id for x in boards]
            yield (value, label, selected)

    def process(self, formdata, data=unset_value, **kwargs):
        print formdata
        return super(MultiCheckboxField, self).process(formdata, data, **kwargs)
