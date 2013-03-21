from django.forms import ModelForm, ModelChoiceField, CharField
from django.core.exceptions import ValidationError

from repository.models import *


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
            sites = Site.objects.filter(project__id=project_id).order_by('site_name')
            if not sites:
                raise ValidationError('Error creating panel. There are no sites for this project. A panel must belong to a project site.')
            self.fields['site'] = ModelChoiceField(sites)


class PanelEditForm(ModelForm):
    class Meta:
        model = Panel
        exclude = ('site',)  # don't allow editing of the site for an existing panel


# yes it's the same as PanelEditForm, but the class names provide context
class PanelFromSampleForm(ModelForm):
    class Meta:
        model = Panel
        exclude = ('site',)


class PanelParameterMapFromSampleForm(ModelForm):
    fcs_opt_text = CharField(required=False)
    parameter = ModelChoiceField(queryset=Parameter.objects.order_by('parameter_short_name'))

    class Meta:
        model = PanelParameterMap
        fields = ('fcs_text', 'fcs_opt_text', 'parameter', 'value_type')


class PanelParameterMapForm(ModelForm):
    class Meta:
        model = PanelParameterMap
        fields = ('fcs_text', 'parameter', 'value_type')
        exclude = ('panel',)


class SubjectForm(ModelForm):
    class Meta:
        model = Subject
        exclude = ('project',)


class SampleForm(ModelForm):
    class Meta:
        model = Sample
        exclude = ('original_filename', 'sha1')

    def __init__(self, *args, **kwargs):
        # pop our 'project_id' key since parent's init is not expecting it
        project_id = kwargs.pop('project_id', None)

        # now it's safe to call the parent init
        super(SampleForm, self).__init__(*args, **kwargs)

        # finally, make sure only project's subjects, sites, and visit types are the available choices
        if project_id:
            subjects = Subject.objects.filter(project__id=project_id).order_by('subject_id')
            self.fields['subject'] = ModelChoiceField(subjects)

            sites = Site.objects.filter(project__id=project_id).order_by('site_name')
            self.fields['site'] = ModelChoiceField(sites, required=False)

            visit_types = ProjectVisitType.objects.filter(project__id=project_id).order_by('visit_type_name')
            self.fields['visit'] = ModelChoiceField(visit_types, required=False)


class SampleSubjectForm(ModelForm):
    class Meta:
        model = Sample
        exclude = ('subject', 'original_filename', 'sha1')

    def __init__(self, *args, **kwargs):
        # pop our 'project_id' key since parent's init is not expecting it
        project_id = kwargs.pop('project_id', None)

        # now it's safe to call the parent init
        super(SampleSubjectForm, self).__init__(*args, **kwargs)

        # finally, make sure only project's site and visit types are the available choices
        if project_id:
            sites = Site.objects.filter(project__id=project_id)
            self.fields['site'] = ModelChoiceField(sites)

            visit_types = ProjectVisitType.objects.filter(project__id=project_id)
            self.fields['visit'] = ModelChoiceField(visit_types)


class SampleEditForm(ModelForm):
    class Meta:
        model = Sample
        exclude = ('subject', 'original_filename', 'sample_file', 'sha1')

    def __init__(self, *args, **kwargs):
        # pop our 'project_id' key since parent's init is not expecting it
        project_id = kwargs.pop('project_id', None)

        # now it's safe to call the parent init
        super(SampleEditForm, self).__init__(*args, **kwargs)

        # finally, make sure only project's visit types are the available choices
        if project_id:
            sites = Site.objects.filter(project__id=project_id)
            self.fields['site'] = ModelChoiceField(sites)

            visit_types = ProjectVisitType.objects.filter(project__id=project_id)
            self.fields['visit'] = ModelChoiceField(visit_types)


class CompensationForm(ModelForm):
    class Meta:
        model = Compensation
        exclude = ('original_filename', 'matrix_text')

    def __init__(self, *args, **kwargs):
        # pop our 'project_id' key since parent's init is not expecting it
        project_id = kwargs.pop('project_id', None)

        # now it's safe to call the parent init
        super(CompensationForm, self).__init__(*args, **kwargs)

        # finally, make sure only project's sites are the available choices
        if project_id:
            sites = Site.objects.filter(project__id=project_id).order_by('site_name')
            self.fields['site'] = ModelChoiceField(sites, required=True)
