__author__ = 'swhite'
from repository.models import *

from django.forms import ModelForm, ModelChoiceField
from django.core.exceptions import ValidationError

class ProjectForm(ModelForm):
    class Meta:
        model = Project

class SiteForm(ModelForm):
    class Meta:
        model = Site
        exclude = ('project',)

class ProjectVisitTypeForm(ModelForm):
    class Meta:
        model = ProjectVisitType
        exclude = ('project',)

class PanelForm(ModelForm):
    class Meta:
        model = Panel

    def __init__(self, *args, **kwargs):
        # pop our 'project_id' key since parent's init is not expecting it
        project_id = kwargs.pop('project_id', None)

        # now it's safe to call the parent init
        super(PanelForm, self).__init__(*args, **kwargs)

        # finally, the reason we're here...make sure only the project's sites are the available choices
        if project_id:
            sites = Site.objects.filter(project__id=project_id)
            if not sites:
                raise ValidationError('Error creating panel. There are no sites for this project. A panel must belong to a project site.')
            self.fields['site'] = ModelChoiceField(sites)

class PanelParameterMapForm(ModelForm):
    class Meta:
        model = PanelParameterMap
        exclude = ('panel',)


class SubjectForm(ModelForm):
    class Meta:
        model = Subject
        exclude = ('project',)


class SampleForm(ModelForm):
    class Meta:
        model = Sample
        exclude = ('subject','original_filename')

    def __init__(self, *args, **kwargs):
        # pop our 'project_id' key since parent's init is not expecting it
        project_id = kwargs.pop('project_id', None)

        # now it's safe to call the parent init
        super(SampleForm, self).__init__(*args, **kwargs)

        # finally, make sure only project's visit types are the available choices
        if project_id:
            visit_types = ProjectVisitType.objects.filter(project__id=project_id)
            self.fields['visit'] = ModelChoiceField(visit_types)


class SampleEditForm(ModelForm):
    class Meta:
        model = Sample
        exclude = ('subject', 'original_filename', 'sample_file')

    def __init__(self, *args, **kwargs):
        # pop our 'project_id' key since parent's init is not expecting it
        project_id = kwargs.pop('project_id', None)

        # now it's safe to call the parent init
        super(SampleEditForm, self).__init__(*args, **kwargs)

        # finally, make sure only project's visit types are the available choices
        if project_id:
            visit_types = ProjectVisitType.objects.filter(project__id=project_id)
            self.fields['visit'] = ModelChoiceField(visit_types)
