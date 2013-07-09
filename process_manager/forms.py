from django.forms import Form, ModelForm

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