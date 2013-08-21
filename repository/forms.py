from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from guardian.forms import UserObjectPermissionsForm

from repository.models import *


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project


class CustomUserObjectPermissionForm(UserObjectPermissionsForm):
    """
    Subclass guardian's UserObjectPermissionsForm to exclude
    Django's default model permissions.
    """
    def get_obj_perms_field_choices(self):
        choices = super(CustomUserObjectPermissionForm, self).get_obj_perms_field_choices()
        return list(set(choices).intersection(self.obj._meta.permissions))


class AntibodyForm(forms.ModelForm):
    class Meta:
        model = Antibody


class FluorochromeForm(forms.ModelForm):
    class Meta:
        model = Fluorochrome


class ParameterForm(forms.ModelForm):
    class Meta:
        model = Parameter


class ParameterAntibodyMapForm(forms.ModelForm):
    class Meta:
        model = ParameterAntibodyMap
        exclude = ('parameter',)


class ParameterFluorochromeMapForm(forms.ModelForm):
    class Meta:
        model = ParameterFluorochromeMap
        exclude = ('parameter',)


class SpecimenForm(forms.ModelForm):
    class Meta:
        model = Specimen


class UserSelectForm(forms.Form):
    username = forms.CharField(label='Username')

    def __init__(self, *args, **kwargs):
        # pop our 'project_id' key since parent's init is not expecting it
        project_id = kwargs.pop('project_id', None)

        # now it's safe to call the parent init
        super(UserSelectForm, self).__init__(*args, **kwargs)

        # finally, the reason we're here...
        # make sure only the project's sites are the available choices
        if project_id:
            sites = Site.objects.filter(project__id=project_id).order_by('site_name')
            self.fields['site'] = forms.ModelChoiceField(
                sites,
                required=False,
                empty_label='Project Level - All Sites')

    def clean(self):
        """
        Validate user exists.
        """
        if not self.cleaned_data.has_key('username'):
            raise ValidationError("No user specified.")

        try:
            user = User.objects.get(username=self.cleaned_data['username'])
        except ObjectDoesNotExist:
            raise ValidationError("User does not exist.")

        self.cleaned_data['user'] = user.id

        return self.cleaned_data #never forget this! ;o)


class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        exclude = ('project',)


class ProjectVisitTypeForm(forms.ModelForm):
    class Meta:
        model = ProjectVisitType
        exclude = ('project',)


class PanelForm(forms.ModelForm):
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
            self.fields['site'] = forms.ModelChoiceField(sites)


class PanelEditForm(forms.ModelForm):
    class Meta:
        model = Panel
        exclude = ('site',)  # don't allow editing of the site for an existing panel


# yes it's the same as PanelEditForm, but the class names provide context
class PanelFromSampleForm(forms.ModelForm):
    class Meta:
        model = Panel
        exclude = ('site',)


class PanelParameterMapFromSampleForm(forms.ModelForm):
    fcs_opt_text = forms.CharField(required=False)
    parameter = forms.ModelChoiceField(queryset=Parameter.objects.order_by('parameter_short_name'))

    class Meta:
        model = PanelParameterMap
        fields = ('fcs_text', 'fcs_opt_text', 'parameter', 'value_type')


class PanelParameterMapForm(forms.ModelForm):
    class Meta:
        model = PanelParameterMap
        fields = ('fcs_text', 'parameter', 'value_type')
        exclude = ('panel',)


class SubjectGroupForm(forms.ModelForm):
    class Meta:
        model = SubjectGroup
        exclude = ('project',)


class SubjectForm(forms.ModelForm):
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
            self.fields['subject_group'] = forms.ModelChoiceField(subject_groups)


class SampleGroupForm(forms.ModelForm):
    class Meta:
        model = SampleGroup


class SampleForm(forms.ModelForm):
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
            self.fields['subject'] = forms.ModelChoiceField(subjects)

            # we also need to limit the sites to those that the user has 'add' permission for
            project = Project.objects.get(id=project_id)
            sites = Site.objects.get_sites_user_can_add(request.user, project).order_by('site_name')
            self.fields['site'] = forms.ModelChoiceField(sites)

            visit_types = ProjectVisitType.objects.filter(project__id=project_id).order_by('visit_type_name')
            self.fields['visit'] = forms.ModelChoiceField(visit_types)


class SampleSubjectForm(forms.ModelForm):
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
            self.fields['site'] = forms.ModelChoiceField(user_sites)

            visit_types = ProjectVisitType.objects.filter(project__id=project_id)
            self.fields['visit'] = forms.ModelChoiceField(visit_types)


class SampleSiteForm(forms.ModelForm):
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
            self.fields['subject'] = forms.ModelChoiceField(subjects)

            visit_types = ProjectVisitType.objects.filter(project__id=project_id)
            self.fields['visit'] = forms.ModelChoiceField(visit_types)


class SampleEditForm(forms.ModelForm):
    class Meta:
        model = Sample
        exclude = ('original_filename', 'sample_file', 'sha1')

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
            self.fields['site'] = forms.ModelChoiceField(sites)

            visit_types = ProjectVisitType.objects.filter(project__id=project_id)
            self.fields['visit'] = forms.ModelChoiceField(visit_types)


class CompensationForm(forms.ModelForm):
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
            self.fields['site'] = forms.ModelChoiceField(sites)


class SampleSetForm(forms.ModelForm):
    class Meta:
        model = SampleSet
        exclude = ('project',)

    def __init__(self, *args, **kwargs):
        # pop our 'project_id' key since parent's init is not expecting it
        project_id = kwargs.pop('project_id', None)

        # now it's safe to call the parent init
        super(SampleSetForm, self).__init__(*args, **kwargs)

        # finally, make sure the available choices belong to the project
        if project_id:
            sites = Site.objects.filter(project_id=project_id)
            self.fields['sites'] = forms.ModelMultipleChoiceField(
                sites,
                required=False,
                widget=forms.widgets.CheckboxSelectMultiple()
            )

            subjects = Subject.objects.filter(project_id=project_id)
            self.fields['subjects'] = forms.ModelMultipleChoiceField(
                subjects,
                required=False,
                widget=forms.widgets.CheckboxSelectMultiple()
            )

            visit_types = ProjectVisitType.objects.filter(project_id=project_id)
            self.fields['visit_types'] = forms.ModelMultipleChoiceField(
                visit_types,
                required=False,
                widget=forms.widgets.CheckboxSelectMultiple()
            )

            specimens = Specimen.objects.all()
            self.fields['specimens'] = forms.ModelMultipleChoiceField(
                specimens,
                required=False,
                widget=forms.widgets.CheckboxSelectMultiple()
            )

            # and now some foo to get the distinct list of parameter+value_type
            # from all categorized samples in the project.
            spm = SampleParameterMap.objects.filter(sample__subject__project_id=project_id)
            unique_param_combos = spm.values('parameter__parameter_short_name','value_type__value_type_short_name')\
                .exclude(parameter=None)\
                .distinct()\
                .order_by('parameter','value_type')
            # and combine the param + value type to one string per parameter
            parameter_list = []
            for p in unique_param_combos:
                parameter_list.append(
                    (
                        p['parameter__parameter_short_name'] + '-' + p['value_type__value_type_short_name'],
                        p['parameter__parameter_short_name'] + '-' + p['value_type__value_type_short_name']
                    )
                )
            self.fields['parameters'] = forms.MultipleChoiceField(
                choices=parameter_list,
                required=False,
                widget=forms.widgets.CheckboxSelectMultiple()
            )

    def clean(self):
        """
        Validate all samples belong to the same project, and that
        at least one sample is included in the set.
        """
        if not self.cleaned_data.has_key('samples'):
            raise ValidationError("There must be at least one sample in a set.")

        samples = self.cleaned_data['samples']
        matching_count = samples.filter(subject__project_id=self.instance.project_id).count()
        
        if samples.count() < 1:
            raise ValidationError("A set must contain at least one sample.")
        elif samples.count() != matching_count:
            raise ValidationError("A set must contain samples from the same project.")

        return self.cleaned_data #never forget this! ;o)