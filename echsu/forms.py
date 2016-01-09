from wtforms_alchemy import model_form_factory
from wtforms_tornado import Form

from echsu.models import Message

ModelForm = model_form_factory(Form)


