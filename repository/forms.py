__author__ = 'swhite'
from repository.models import *

from django.forms import ModelForm

class ProjectForm(ModelForm):
    class Meta:
        model = Project
