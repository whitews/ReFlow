from django.forms import Form, ModelForm, ModelChoiceField, CharField, BooleanField
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from repository.models import *


class ProjectForm(ModelForm):
    class Meta:
        model = Project


class AntibodyForm(ModelForm):
    class Meta:
        model = Antibody


class FluorochromeForm(ModelForm):
    class Meta:
        model = Fluorochrome


class ParameterForm(ModelForm):
    class Meta:
        model = Parameter


class ParameterAntibodyMapForm(ModelForm):
    class Meta:
        model = ParameterAntibodyMap
        exclude = ('parameter',)


class ParameterFluorochromeMapForm(ModelForm):
    class Meta:
        model = ParameterFluorochromeMap
        exclude = ('parameter',)


class SpecimenForm(ModelForm):
    class Meta:
        model = Specimen


class UserSelectForm(Form):
    user = ModelChoiceField(label='User', queryset=User.objects.order_by('username'))

    def __init__(self, *args, **kwargs):
        # pop our 'project_id' key since parent's init is not expecting it
        project_id = kwargs.pop('project_id', None)

        # now it's safe to call the parent init
        super(UserSelectForm, self).__init__(*args, **kwargs)

        # finally, the reason we're here...
        # make sure only the project's sites are the available choices
        if project_id:
            sites = Site.objects.filter(project__id=project_id).order_by('site_name')
            self.fields['site'] = ModelChoiceField(
                sites,
                required=False,
                empty_label='Project Level - All Sites')


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

        # finally, the reason we're here...
        # make sure only the project's sites are the available choices
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

    def __init__(self, *args, **kwargs):
        # pop our 'project_id' key since parent's init is not expecting it
        project_id = kwargs.pop('project_id', None)

        # likewise for 'request' arg
        request = kwargs.pop('request', None)

        # now it's safe to call the parent init
        super(SubjectForm, self).__init__(*args, **kwargs)

        # finally, make sure only project's subject groups are the available choices
        if project_id:
            subject_groups = SubjectGroup.objects.filter(project__id=project_id)
            self.fields['subject_group'] = ModelChoiceField(subject_groups)

class SampleForm(ModelForm):
    class Meta:
        model = Sample
        exclude = ('original_filename', 'sha1')

    def __init__(self, *args, **kwargs):
        # pop our 'project_id' key since parent's init is not expecting it
        project_id = kwargs.pop('project_id', None)

        # likewise for 'request' arg
        request = kwargs.pop('request', None)

        # now it's safe to call the parent init
        super(SampleForm, self).__init__(*args, **kwargs)

        # finally, make sure only project's subjects, sites, and visit types
        # are the available choices
        if project_id:
            subjects = Subject.objects.filter(project__id=project_id).order_by('subject_id')
            self.fields['subject'] = ModelChoiceField(subjects)

            # we also need to limit the sites to those that the user has 'add' permission for
            project = Project.objects.get(id=project_id)
            sites = Site.objects.get_sites_user_can_add(request.user, project).order_by('site_name')
            self.fields['site'] = ModelChoiceField(sites)

            visit_types = ProjectVisitType.objects.filter(project__id=project_id).order_by('visit_type_name')
            self.fields['visit'] = ModelChoiceField(visit_types)


class SampleSubjectForm(ModelForm):
    class Meta:
        model = Sample
        exclude = ('subject', 'original_filename', 'sha1')

    def __init__(self, *args, **kwargs):
        # pop our 'project_id' key since parent's init is not expecting it
        project_id = kwargs.pop('project_id', None)

        # likewise for 'request' arg
        request = kwargs.pop('request', None)

        # now it's safe to call the parent init
        super(SampleSubjectForm, self).__init__(*args, **kwargs)

        # finally, make sure only project's sites and visit types are the available choices
        if project_id:
            # we also need to limit the sites to those that the user has 'add' permission for
            project = Project.objects.get(id=project_id)
            user_sites = Site.objects.get_sites_user_can_add(request.user, project).order_by('site_name')
            self.fields['site'] = ModelChoiceField(user_sites)

            visit_types = ProjectVisitType.objects.filter(project__id=project_id)
            self.fields['visit'] = ModelChoiceField(visit_types)


class SampleSiteForm(ModelForm):
    class Meta:
        model = Sample
        exclude = ('site', 'original_filename', 'sha1')

    def __init__(self, *args, **kwargs):
        # pop our 'project_id' key since parent's init is not expecting it
        project_id = kwargs.pop('project_id', None)

        # likewise for 'request' arg
        request = kwargs.pop('request', None)

        # now it's safe to call the parent init
        super(SampleSiteForm, self).__init__(*args, **kwargs)

        # finally, make sure only project's subjects and visit types are the available choices
        if project_id:
            subjects = Subject.objects.filter(project__id=project_id)
            self.fields['subject'] = ModelChoiceField(subjects)

            visit_types = ProjectVisitType.objects.filter(project__id=project_id)
            self.fields['visit'] = ModelChoiceField(visit_types)


class SampleEditForm(ModelForm):
    class Meta:
        model = Sample
        exclude = ('subject', 'original_filename', 'sample_file', 'sha1')

    def __init__(self, *args, **kwargs):
        # pop our 'project_id' key since parent's init is not expecting it
        project_id = kwargs.pop('project_id', None)

        # likewise for 'request' arg
        request = kwargs.pop('request', None)

        # now it's safe to call the parent init
        super(SampleEditForm, self).__init__(*args, **kwargs)

        # finally, make sure only project's visit types are the available choices
        if project_id:
            project = Project.objects.get(id=project_id)
            sites = Site.objects.get_sites_user_can_add(request.user, project).order_by('site_name')
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

        # likewise for 'request' arg
        request = kwargs.pop('request', None)

        # now it's safe to call the parent init
        super(CompensationForm, self).__init__(*args, **kwargs)

        # finally, make sure only project's sites are the available choices
        if project_id:
            project = Project.objects.get(id=project_id)
            sites = Site.objects.get_sites_user_can_add(request.user, project).order_by('site_name')
            self.fields['site'] = ModelChoiceField(sites)
