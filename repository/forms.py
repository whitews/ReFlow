from collections import Counter
from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from guardian.forms import UserObjectPermissionsForm

from repository.models import *


class StainingForm(forms.ModelForm):
    class Meta:
        model = Staining


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project


class CustomUserObjectPermissionForm(UserObjectPermissionsForm):
    """
    Subclass guardian's UserObjectPermissionsForm to exclude
    Django's default model permissions.
    """
    def get_obj_perms_field_widget(self):
        """
        Override to select a CheckboxSelectMultiple (default is SelectMultiple).
        """
        return forms.CheckboxSelectMultiple

    def get_obj_perms_field_choices(self):
        choices = super(CustomUserObjectPermissionForm, self).get_obj_perms_field_choices()
        return list(set(choices).intersection(self.obj._meta.permissions))


class AntibodyForm(forms.ModelForm):
    class Meta:
        model = Antibody


class FluorochromeForm(forms.ModelForm):
    class Meta:
        model = Fluorochrome


class ProjectPanelForm(forms.ModelForm):
    class Meta:
        model = ProjectPanel
        exclude = ('project',)  # don't allow changing the parent project
        widgets = {
            'panel_description': forms.Textarea(attrs={'cols': 20, 'rows': 5}),
        }


ProjectPanelParameterAntibodyFormSet = inlineformset_factory(
    ProjectPanelParameter,
    ProjectPanelParameterAntibody,
    extra=1,
    can_delete=False)


class BaseProjectPanelParameterFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        # allow the super class to create the fields as usual
        super(BaseProjectPanelParameterFormSet, self).add_fields(form, index)

        # create the nested formset
        try:
            instance = self.get_queryset()[index]
            pk_value = instance.pk
        except IndexError:
            instance=None
            pk_value = form.prefix

        # store the formset in the .nested property
        data = self.data if self.data and index is not None else None
        form.nested = [
            ProjectPanelParameterAntibodyFormSet(
                data=data,
                instance=instance,
                prefix=pk_value)]

    def clean(self):
        """
        Validate the panel:
            - No duplicate antibodies in a parameter
            - No fluorochromes in a scatter parameter
            - No antibodies in a scatter parameter
            - Fluoroscent parameter must specify a fluorochrome
            - No duplicate fluorochrome + value type combinations
            - No duplicate forward scatter + value type combinations
            - No duplicate side scatter + value type combinations
        """
        param_counter = Counter()

        for form in self.forms:
            ab_formset = form.nested[0]

            # check for duplicate antibodies in a parameter
            ab_set = set()
            for ab_form in ab_formset.forms:
                new_ab_id = ab_form.data[ab_form.add_prefix('antibody')]
                if new_ab_id:  # if it's not empty string
                    if new_ab_id in ab_set:
                        raise ValidationError("A parameter cannot have duplicate antibodies.")
                    else:
                        ab_set.add(new_ab_id)

            # parameter type is required
            param_type_id = form.data[form.add_prefix('parameter_type')]
            if not param_type_id:
                raise ValidationError("Parameter type is required")
            param_type = ParameterType.objects.get(id=param_type_id)

            # value type is required
            value_type_id = form.data[form.add_prefix('parameter_value_type')]
            if not value_type_id:
                raise ValidationError("Value type is required")
            value_type = ParameterValueType.objects.get(id=value_type_id)

            fluorochrome_id = form.data[form.add_prefix('fluorochrome')]

            # check for fluoro or antibodies in scatter channels
            if 'scatter' in param_type.parameter_type_name.lower() and fluorochrome_id:
                raise ValidationError("A scatter channel cannot have a fluorochrome.")
            if 'scatter' in param_type.parameter_type_name.lower() and len(ab_set) > 0:
                raise ValidationError("A scatter channel cannot have an antibody.")

            # check that fluorescence channels specify a fluoro
            if 'fluor' in param_type.parameter_type_name.lower() and not fluorochrome_id:
                raise ValidationError("A fluoroscence channel must specify a fluorochrome.")

            # make a list of the combination for use in the Counter
            param_components = [param_type, value_type]
            if fluorochrome_id:
                param_components.append(fluorochrome_id)

            param_counter.update([tuple(sorted(param_components))])

        # check for duplicate parameters
        if max(param_counter.values()) > 1:
            raise ValidationError("Cannot have duplicate parameters")


ParameterFormSet = inlineformset_factory(
    ProjectPanel,
    ProjectPanelParameter,
    formset=BaseProjectPanelParameterFormSet,
    extra=1,
    can_delete=False
)


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


class VisitTypeForm(forms.ModelForm):
    class Meta:
        model = VisitType
        exclude = ('project',)


class PreSitePanelForm(forms.ModelForm):
    fcs_file = forms.FileField(label="FCS file")

    class Meta:
        model = SitePanel
        exclude = ('site',)

    def __init__(self, *args, **kwargs):
        # pop our 'project_id' key since parent's init is not expecting it
        project_id = kwargs.pop('project_id', None)

        # now it's safe to call the parent init
        super(PreSitePanelForm, self).__init__(*args, **kwargs)

        # finally, the reason we're here...
        # make sure only the project's panels are the available choices
        if project_id:
            project_panels = ProjectPanel.objects.filter(
                project__id=project_id).order_by('panel_name')
            self.fields['project_panel'] = forms.ModelChoiceField(
                project_panels,
                required=True,)


class SitePanelForm(forms.ModelForm):
    class Meta:
        model = SitePanel
        exclude = ('site',)  # don't allow editing of the site for an existing panel


# yes it's the same as SitePanelEditForm, but the class names provide context
class SitePanelFromSampleForm(forms.ModelForm):
    class Meta:
        model = SitePanel
        exclude = ('site',)


class SitePanelParameterMapFromSampleForm(forms.ModelForm):

    class Meta:
        model = SitePanelParameter
        fields = ('fcs_text', 'fcs_opt_text', 'parameter_value_type')


class SitePanelParameterForm(forms.ModelForm):
    class Meta:
        model = SitePanelParameter
        fields = ('fcs_text', 'fcs_opt_text', 'parameter_value_type')
        exclude = ('site_panel',)


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


class StimulationForm(forms.ModelForm):
    class Meta:
        model = Stimulation
        exclude = ('project',)


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
            subjects = Subject.objects.filter(project__id=project_id).order_by('subject_code')
            self.fields['subject'] = forms.ModelChoiceField(subjects)

            # we also need to limit the sites to those that the user has 'add' permission for
            project = Project.objects.get(id=project_id)
            sites = Site.objects.get_sites_user_can_add(request.user, project).order_by('site_name')
            site_panels = SitePanel.objects.filter(site__in=sites)
            self.fields['site_panel'] = forms.ModelChoiceField(site_panels)

            visit_types = VisitType.objects.filter(project__id=project_id).order_by('visit_type_name')
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

            visit_types = VisitType.objects.filter(project__id=project_id)
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

            visit_types = VisitType.objects.filter(project__id=project_id)
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

            visit_types = VisitType.objects.filter(project__id=project_id)
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

            visit_types = VisitType.objects.filter(project_id=project_id)
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
            spp = SitePanelParameter.objects.filter(site_panel__project_panel__project_id=project_id)
            unique_param_combos = spp.values(
                    'parameter_type__parameter_type_abbreviation',
                    'parameter_value_type__value_type_abbreviation')\
                .distinct()\
                .order_by('parameter_type','parameter_value_type')
            # and combine the param + value type to one string per parameter
            parameter_list = []
            for p in unique_param_combos:
                parameter_list.append(
                    (
                        p['parameter_type__parameter_type_abbreviation'] + '-' + p['parameter_value_type__value_type_abbreviation'],
                        p['parameter_type__parameter_type_abbreviation'] + '-' + p['parameter_value_type__value_type_abbreviation']
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