import re
from django import forms
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from repository.models import Project, Site, \
    Cytometer, Compensation, ProjectPanel, SitePanel, \
    SitePanelParameter, Worker


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