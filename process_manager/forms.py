from django.forms import Form, ModelForm

from process_manager.models import *


class ProcessForm(ModelForm):
    class Meta:
        model = Process


class ProcessInputForm(ModelForm):
    class Meta:
        model = ProcessInput
        exclude = ('process',)