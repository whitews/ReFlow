import re
from django import forms
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.models import User
from guardian.forms import UserObjectPermissionsForm

from repository.models import Project, Site, Subject, VisitType, Sample, \
    Cytometer, Compensation, ProjectPanel, SitePanel, \
    Fluorochrome, Marker, SitePanelParameter, \
    Specimen, SubjectGroup, Stimulation, Worker


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
        choices = super(
            CustomUserObjectPermissionForm, self).get_obj_perms_field_choices()
        return list(set(choices).intersection(self.obj._meta.permissions))


class MarkerForm(forms.ModelForm):
    class Meta:
        model = Marker


class FluorochromeForm(forms.ModelForm):
    class Meta:
        model = Fluorochrome


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
            sites = Site.objects.filter(
                project__id=project_id).order_by('site_name')
            self.fields['site'] = forms.ModelChoiceField(
                sites,
                required=False,
                empty_label='Project Level - All Sites')

    def clean(self):
        """
        Validate user exists.
        """
        if not 'username' in self.cleaned_data:
            raise ValidationError("No user specified.")

        try:
            user = User.objects.get(username=self.cleaned_data['username'])
        except ObjectDoesNotExist:
            raise ValidationError("User does not exist.")

        self.cleaned_data['user'] = user.id

        return self.cleaned_data  # never forget this! ;o)


class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        exclude = ('project',)


class CytometerForm(forms.ModelForm):
    class Meta:
        model = Cytometer

    def __init__(self, *args, **kwargs):
        # pop our 'project_id' key since parent's init is not expecting it
        project_id = kwargs.pop('project_id', None)

        # now it's safe to call the parent init
        super(CytometerForm, self).__init__(*args, **kwargs)

        # finally, make sure only project's sites are the
        # available choices
        if project_id:
            sites = Site.objects.filter(project__id=project_id)

        else:
            sites = Site.objects.none()

        self.fields['site'] = forms.ModelChoiceField(sites)


class VisitTypeForm(forms.ModelForm):
    class Meta:
        model = VisitType
        exclude = ('project',)


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        exclude = ('project',)

    def __init__(self, *args, **kwargs):
        # pop our 'project_id' key since parent's init is not expecting it
        project_id = kwargs.pop('project_id', None)

        # now it's safe to call the parent init
        super(SubjectForm, self).__init__(*args, **kwargs)

        # finally, make sure only project's subject groups are the
        # available choices
        if project_id:
            subject_groups = SubjectGroup.objects.filter(project__id=project_id)
            self.fields['subject_group'] = forms.ModelChoiceField(
                subject_groups)


class StimulationForm(forms.ModelForm):
    class Meta:
        model = Stimulation
        exclude = ('project',)


class SampleEditForm(forms.ModelForm):
    class Meta:
        model = Sample
        exclude = ('original_filename', 'sample_file', 'sha1', 'subsample')

    def __init__(self, *args, **kwargs):
        # pop our 'project_id' key since parent's init is not expecting it
        project_id = kwargs.pop('project_id', None)

        # likewise for 'request' arg
        request = kwargs.pop('request', None)

        # now it's safe to call the parent init
        super(SampleEditForm, self).__init__(*args, **kwargs)

        # finally, make sure only project's visit types are the
        # available choices
        if project_id:
            site_panels = SitePanel.objects.filter(
                site=self.instance.site_panel.site)
            self.fields['site_panel'] = forms.ModelChoiceField(site_panels)

            visit_types = VisitType.objects.filter(project__id=project_id)
            self.fields['visit'] = forms.ModelChoiceField(visit_types)

            stimulations = Stimulation.objects.filter(
                project__id=project_id).order_by('stimulation_name')
            self.fields['stimulation'] = forms.ModelChoiceField(stimulations)

            compensations = Compensation.objects.filter(
                site_panel__site__project__id=project_id).order_by('name')
            self.fields['compensation'] = forms.ModelChoiceField(compensations)


class CompensationForm(forms.ModelForm):
    class Meta:
        model = Compensation
        exclude = ('compensation_file',)

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
            sites = Site.objects.get_sites_user_can_add(
                request.user, project)
            site_panels = SitePanel.objects.filter(site__in=sites)
            self.fields['site_panel'] = forms.ModelChoiceField(site_panels)

    def clean(self):
        """
        Validate compensation matrix matches site panel
        """
        if not 'site_panel' in self.cleaned_data:
            # site panel is required, will get caught
            return self.cleaned_data
        if not 'matrix_text' in self.cleaned_data:
            # matrix text is required, will get caught
            return self.cleaned_data

        try:
            site_panel = SitePanel.objects.get(
                id=self.cleaned_data['site_panel'].id)
        except ObjectDoesNotExist:
            raise ValidationError("Site panel does not exist.")

        # get site panel parameter fcs_text, but just for the fluoro params
        # 'Null', scatter and time don't get compensated
        params = SitePanelParameter.objects.filter(
            site_panel=site_panel).exclude(
                parameter_type__in=['FSC', 'SSC', 'TIM', 'NUL'])

        # parse the matrix text and validate the number of params match
        # the number of fluoro params in the site panel and that the matrix
        # values are numbers (can be exp notation)
        matrix_text = str(self.cleaned_data['matrix_text'])
        matrix_text = matrix_text.splitlines(False)

        # first row should be headers matching the PnN value (fcs_text field)
        # may be tab or comma delimited
        # (spaces can't be delimiters b/c they are allowed in the PnN value)
        headers = re.split('\t|,\s*', matrix_text[0])

        missing_fields = list()
        for p in params:
            if p.fcs_text not in headers:
                missing_fields.append(p.fcs_text)

        if len(missing_fields) > 0:
            self._errors["matrix_text"] = \
                "Missing fields: %s" % ", ".join(missing_fields)
            return self.cleaned_data

        if len(headers) > params.count():
            self._errors["matrix_text"] = "Too many parameters"
            return self.cleaned_data

        # the header of matrix text adds a row
        if len(matrix_text) > params.count() + 1:
            self._errors["matrix_text"] = "Too many rows"
            return self.cleaned_data
        elif len(matrix_text) < params.count() + 1:
            self._errors["matrix_text"] = "Too few rows"
            return self.cleaned_data

        # parse matrix
        for line in matrix_text[1:]:
            line_values = re.split('\t|,', line)
            for i, value in enumerate(line_values):
                try:
                    line_values[i] = float(line_values[i])
                except ValueError:
                    self._errors["matrix_text"] = \
                        "%s is an invalid matrix value" % line_values[i]
            if len(line_values) > len(params):
                self._errors["matrix_text"] = \
                    "Too many values in line: %s" % line
                return self.cleaned_data
            elif len(line_values) < len(params):
                self._errors["matrix_text"] = \
                    "Too few values in line: %s" % line
                return self.cleaned_data

        return self.cleaned_data  # never forget this! ;o)


class WorkerForm(forms.ModelForm):
    class Meta:
        model = Worker


class SampleFilterForm(forms.Form):
    """
    Note the naming of these fields corresponds to the REST API
    URL parameter filter text strings for the various Sample relationships
    See the custom filter in the SampleList in api_views.py
    """

    project_panel = forms.ModelMultipleChoiceField(
        queryset=ProjectPanel.objects.none(),
        required=False,
        widget=forms.widgets.CheckboxSelectMultiple())
    site = forms.ModelMultipleChoiceField(
        queryset=Site.objects.none(),
        required=False,
        widget=forms.widgets.CheckboxSelectMultiple())
    site_panel = forms.ModelMultipleChoiceField(
        queryset=SitePanel.objects.none(),
        required=False,
        widget=forms.widgets.CheckboxSelectMultiple())
    subject = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.none(),
        required=False,
        widget=forms.widgets.CheckboxSelectMultiple())
    subject_group = forms.ModelMultipleChoiceField(
        queryset=SubjectGroup.objects.none(),
        required=False,
        widget=forms.widgets.CheckboxSelectMultiple())
    visit = forms.ModelMultipleChoiceField(
        queryset=VisitType.objects.none(),
        required=False,
        widget=forms.widgets.CheckboxSelectMultiple())
    stimulation = forms.ModelMultipleChoiceField(
        queryset=Stimulation.objects.none(),
        required=False,
        widget=forms.widgets.CheckboxSelectMultiple())
    cytometer = forms.ModelMultipleChoiceField(
        queryset=Cytometer.objects.none(),
        required=False,
        widget=forms.widgets.CheckboxSelectMultiple())

    def __init__(self, *args, **kwargs):
        # pop 'project_id' & 'request' keys, parent init doesn't expect them
        project_id = kwargs.pop('project_id', None)
        request = kwargs.pop('request', None)

        # now it's safe to call the parent init
        super(SampleFilterForm, self).__init__(*args, **kwargs)

        # finally, make sure the available choices belong to the project
        if project_id:
            project = Project.objects.get(id=project_id)

            project_panels = ProjectPanel.objects.filter(project=project)
            self.fields['project_panel'].queryset = project_panels

            sites = Site.objects.get_sites_user_can_view(
                request.user,
                project=project
            )
            self.fields['site'].queryset = sites

            site_panels = SitePanel.objects.filter(site__in=sites)
            self.fields['site_panel'].queryset = site_panels

            subject_groups = SubjectGroup.objects.filter(project_id=project_id)
            self.fields['subject_group'].queryset = subject_groups

            self.fields['subject'].queryset = Subject.objects.filter(
                project_id=project_id
            )

            self.fields['visit'].queryset = VisitType.objects.filter(
                project_id=project_id
            )

            self.fields['stimulation'].queryset = Stimulation.objects.filter(
                project_id=project_id
            )

            cytometers = Cytometer.objects.filter(site__in=sites)
            self.fields['cytometer'].queryset = cytometers


class BeadFilterForm(forms.Form):
    """
    Note the naming of these fields corresponds to the REST API
    URL parameter filter text strings for the various Sample relationships
    See the custom filter in the SampleList in api_views.py
    """

    project_panel = forms.ModelMultipleChoiceField(
        queryset=ProjectPanel.objects.none(),
        required=False,
        widget=forms.widgets.CheckboxSelectMultiple())
    site = forms.ModelMultipleChoiceField(
        queryset=Site.objects.none(),
        required=False,
        widget=forms.widgets.CheckboxSelectMultiple())
    site_panel = forms.ModelMultipleChoiceField(
        queryset=SitePanel.objects.none(),
        required=False,
        widget=forms.widgets.CheckboxSelectMultiple())
    cytometer = forms.ModelMultipleChoiceField(
        queryset=Cytometer.objects.none(),
        required=False,
        widget=forms.widgets.CheckboxSelectMultiple())

    def __init__(self, *args, **kwargs):
        # pop 'project_id' & 'request' keys, parent init doesn't expect them
        project_id = kwargs.pop('project_id', None)
        request = kwargs.pop('request', None)

        # now it's safe to call the parent init
        super(BeadFilterForm, self).__init__(*args, **kwargs)

        # finally, make sure the available choices belong to the project
        if project_id:
            project = Project.objects.get(id=project_id)

            project_panels = ProjectPanel.objects.filter(project=project)
            self.fields['project_panel'].queryset = project_panels

            sites = Site.objects.get_sites_user_can_view(
                request.user,
                project=project
            )
            self.fields['site'].queryset = sites

            site_panels = SitePanel.objects.filter(site__in=sites)
            self.fields['site_panel'].queryset = site_panels

            cytometers = Cytometer.objects.filter(site__in=sites)
            self.fields['cytometer'].queryset = cytometers