from django import forms
from django.forms import ModelForm

from process_manager.models import *


class ProcessForm(ModelForm):
    class Meta:
        model = Process


class ProcessInputForm(ModelForm):
    class Meta:
        model = ProcessInput
        exclude = ('process',)


class WorkerForm(ModelForm):
    class Meta:
        model = Worker


class RegisterProcessToWorkerForm(ModelForm):
    class Meta:
        model = WorkerProcessMap
        exclude = ('worker',)


class ProcessRequestForm(ModelForm):
    class Meta:
        model = ProcessRequest
        exclude = ('process', 'request_user', 'completion_date', 'worker', 'status')


class ProcessRequestInputValueForm(ModelForm):
    value_label = forms.CharField(widget=forms.HiddenInput())
    process_input = forms.ModelChoiceField(
        queryset=ProcessInput.objects.all(),
        widget=forms.HiddenInput())

    class Meta:
        model = ProcessRequestInputValue
        exclude = ('process_request',)