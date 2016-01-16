from wtforms import SelectMultipleField

from wtforms import widgets
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
            selected = self.coerce(value) in [x.id for x in boards]
            yield (value, label, selected)