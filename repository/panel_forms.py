from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.core.exceptions import ValidationError
from collections import Counter

from repository.models import \
    Marker, \
    Project, \
    Site, \
    ProjectPanel, \
    SitePanel, \
    ProjectPanelParameter, \
    ProjectPanelParameterMarker,\
    SitePanelParameter, \
    SitePanelParameterMarker


class PreSitePanelForm(forms.ModelForm):
    fcs_file = forms.FileField(label="FCS file")

    class Meta:
        model = SitePanel

    def __init__(self, *args, **kwargs):
        # pop our 'project_id' key since parent's init is not expecting it
        project_id = kwargs.pop('project_id', None)

        # likewise for 'request' arg
        request = kwargs.pop('request', None)

        # now it's safe to call the parent init
        super(PreSitePanelForm, self).__init__(*args, **kwargs)

        # finally, the reason we're here...
        # make sure only the project's panels are the available choices
        # and that only user sites are available
        if project_id:
            project_panels = ProjectPanel.objects.filter(
                project__id=project_id).order_by('panel_name')
            self.fields['project_panel'] = forms.ModelChoiceField(
                project_panels,
                required=True,)

            # we also need to limit the sites to those that the user has '
            # add' permission for
            project = Project.objects.get(id=project_id)
            user_sites = Site.objects.get_sites_user_can_add(
                request.user, project).order_by('site_name')
            self.fields['site'] = forms.ModelChoiceField(user_sites)


class SitePanelForm(forms.ModelForm):
    class Meta:
        model = SitePanel


class EditSitePanelForm(forms.ModelForm):
    class Meta:
        model = SitePanel
        exclude = ('project_panel',)


class SitePanelParameterMapFromSampleForm(forms.ModelForm):
    class Meta:
        model = SitePanelParameter
        fields = ('fcs_text', 'fcs_opt_text', 'parameter_value_type')


class SitePanelParameterForm(forms.ModelForm):
    class Meta:
        model = SitePanelParameter
        fields = (
            'fcs_number',
            'fcs_text',
            'fcs_opt_text',
            'parameter_type',
            'parameter_value_type',
            'fluorochrome')
        exclude = ('site_panel',)

    def __init__(self, *args, **kwargs):
        super(SitePanelParameterForm, self).__init__(*args, **kwargs)
        self.fields['parameter_type'].widget.attrs['class'] = 'param_type'


class BaseProjectPanelParameterFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        self.can_delete = True
        # allow the super class to create the fields as usual
        super(BaseProjectPanelParameterFormSet, self).add_fields(form, index)

        # create the nested formset
        try:
            instance = self.get_queryset()[index]
            pk_value = instance.pk
        except IndexError:
            instance = None
            pk_value = form.prefix

        # store the formset in the .nested property
        data = self.data if self.data and index is not None else None
        form.nested = [
            ProjectPanelParameterMarkerFormSet(
                data=data,
                instance=instance,
                prefix=pk_value)]

    def clean(self):
        """
        Validate the panel:
            - No duplicate markers in a parameter
            - No fluorochromes in a scatter parameter
            - No markers in a scatter parameter
            - Fluoroscent parameter must specify a fluorochrome
            - No duplicate fluorochrome + value type combinations
            - No duplicate forward scatter + value type combinations
            - No duplicate side scatter + value type combinations
        """
        param_counter = Counter()
        staining = self.instance.staining
        if staining == 'FS':
            can_have_uns = False
            can_have_iso = False
        elif staining == 'FM':
            can_have_uns = True
            can_have_iso = False
        elif staining == 'IS':
            can_have_uns = False
            can_have_iso = True
        elif staining == 'US':
            can_have_uns = True
            can_have_iso = False
        else:
            raise ValidationError(
                "Invalid staining type '%s'" % staining)

        for form in self.forms:
            marker_formset = form.nested[0]

            # check for duplicate markers in a parameter
            marker_set = set()
            for marker_form in marker_formset.forms:
                new_marker_id = marker_form.data[marker_form.add_prefix('marker')]
                if new_marker_id:  # if it's not empty string
                    if new_marker_id in marker_set:
                        raise ValidationError(
                            "A parameter cannot have duplicate markers.")
                    else:
                        marker_set.add(new_marker_id)

            # parameter type is required
            param_type = form.data[form.add_prefix('parameter_type')]
            if not param_type:
                raise ValidationError("Function is required")
            if param_type == 'UNS' and not can_have_uns:
                raise ValidationError(
                    "Only FMO & Unstained panels can include an " +
                    "unstained parameter")
            if param_type == 'ISO' and not can_have_iso:
                raise ValidationError(
                    "Only Isotype control panels can include an " +
                    "isotype control parameter")

            # value type is NOT required for project panels,
            # allows site panel implementations to have different values types
            value_type = form.data[form.add_prefix('parameter_value_type')]
            if not value_type:
                value_type = None

            fluorochrome_id = form.data[form.add_prefix('fluorochrome')]

            # exclusion must be a fluorescence channel
            if param_type == 'EXC' and not fluorochrome_id:
                raise ValidationError(
                    "An exclusion channel must include a fluorochrome.")

            # check for fluoro or markers in scatter channels
            if param_type == 'FSC' or param_type == 'SSC':
                if fluorochrome_id:
                    raise ValidationError(
                        "A scatter channel cannot have a fluorochrome.")
                if len(marker_set) > 0:
                    raise ValidationError(
                        "A scatter channel cannot have an marker.")

            # check that fluoro-conj-ab channels specify either a fluoro or a
            # marker. If the fluoro is absent it means the project panel
            # allows flexibility in the site panel implementation.
            # TODO: shouldn't marker be required here???
            if param_type == 'FCM':
                if not fluorochrome_id and len(marker_set) == 0:
                    raise ValidationError(
                        "A fluorescence conjugated marker channel must " +
                        "specify either a fluorochrome or a marker.")

            # make a list of the combination for use in the Counter
            param_components = [param_type, value_type]
            if fluorochrome_id:
                param_components.append(fluorochrome_id)
            for marker_id in sorted(marker_set):
                try:
                    marker = Marker.objects.get(id=marker_id)
                except:
                    raise ValidationError("Chosen marker doesn't exist")
                param_components.append(marker.marker_abbreviation)
            param_counter.update([tuple(sorted(param_components))])

        # check for duplicate parameters
        if max(param_counter.values()) > 1:
            error_string = "Duplicate parameters found: "
            for p in param_counter:
                if param_counter[p] > 1:
                    error_string += "(" + ", ".join(p) + ")"
            raise ValidationError(error_string)


class BaseSitePanelParameterFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        # allow the super class to create the fields as usual
        super(BaseSitePanelParameterFormSet, self).add_fields(form, index)

        # create the nested formset
        try:
            instance = self.get_queryset()[index]
            pk_value = instance.pk
        except IndexError:
            instance = None
            pk_value = form.prefix

        # store the formset in the .nested property
        data = self.data if self.data and index is not None else None
        form.nested = [
            SitePanelParameterMarkerFormSet(
                data=data,
                instance=instance,
                prefix=pk_value)]

    def clean(self):
        """
        Validate the panel:
            - No duplicate markers in a parameter
            - No fluorochromes in a scatter parameter
            - No markers in a scatter parameter
            - Fluoroscent parameter must specify a fluorochrome
            - No duplicate fluorochrome + value type combinations
            - No duplicate forward scatter + value type combinations
            - No duplicate side scatter + value type combinations
        Validations against the parent project panel:
            - Ensure all project panel parameters are present
        """
        param_counter = Counter()
        param_dict = {}
        staining = self.instance.project_panel.staining
        if staining == 'FS':
            can_have_uns = True
            can_have_iso = False
        elif staining == 'FM':
            can_have_uns = True
            can_have_iso = False
        elif staining == 'IS':
            can_have_uns = False
            can_have_iso = True
        elif staining == 'US':
            can_have_uns = True
            can_have_iso = False
        else:
            raise ValidationError(
                "Invalid staining type '%s'" % staining)

        for form in self.forms:
            marker_formset = form.nested[0]

            # check for duplicate markers in a parameter
            marker_set = set()
            for marker_form in marker_formset.forms:
                new_marker_id = marker_form.data[marker_form.add_prefix('marker')]
                if new_marker_id:  # if it's not empty string
                    new_marker_id = int(new_marker_id)
                    if new_marker_id in marker_set:
                        raise ValidationError(
                            "A parameter cannot have duplicate markers")
                    else:
                        marker_set.add(new_marker_id)

            # parameter type is required
            param_type = form.data[form.add_prefix('parameter_type')]
            if not param_type:
                raise ValidationError(
                    "Function is required for all parameters")
            if param_type == 'UNS' and not can_have_uns:
                raise ValidationError(
                    "Only Full Stain, FMO, & Unstained panels can " +
                    "include an unstained parameter")
            if param_type == 'ISO' and not can_have_iso:
                raise ValidationError(
                    "Only Isotype control panels can include an " +
                    "isotype control parameter")

            # value type is required
            value_type = form.data[form.add_prefix('parameter_value_type')]
            if not value_type:
                raise ValidationError("Value type is required")

            fluorochrome_id = form.data[form.add_prefix('fluorochrome')]

            # exclusion must be a fluorescence channel
            if param_type == 'EXC' and not fluorochrome_id:
                raise ValidationError(
                    "An exclusion channel must be a fluorescence channel")

            # check for fluoro or markers in scatter channels
            if param_type in ['FSC', 'SSC']:
                if fluorochrome_id:
                    raise ValidationError(
                        "A scatter channel cannot have a fluorochrome")
                if len(marker_set) > 0:
                    raise ValidationError(
                        "A scatter channel cannot have a marker")

            # check that fluoro conjugated ab channels specify either a
            # fluoro OR marker OR both
            if param_type == 'FCM':
                if not fluorochrome_id or len(marker_set) == 0:
                    raise ValidationError(
                        "A fluorescence conjugated marker channel must " +
                        "specify a fluorochrome and at least one marker")

            # Unstained channels can't have a fluoro and must have an marker
            if param_type == 'UNS':
                if fluorochrome_id:
                    raise ValidationError(
                        "Unstained channels CANNOT " +
                        "have a fluorochrome")
                if len(marker_set) == 0:
                    raise ValidationError(
                        "Unstained channels " +
                        "must specify at least one marker")

            # Iso control & Viability channels must have a fluoro and
            # can't have markers
            if param_type == 'ISO':
                if not fluorochrome_id:
                    raise ValidationError(
                        "Isotype control channels must " +
                        "have a fluorochrome")
                if len(marker_set) > 0:
                    raise ValidationError(
                        "Isotype control channels " +
                        "CANNOT have any markers")

            # Time channels cannot have fluoros or markers, must have T value
            if param_type == 'TIM':
                if fluorochrome_id:
                    raise ValidationError(
                        "Time channels " +
                        "CANNOT have a fluorochrome")
                if len(marker_set) > 0:
                    raise ValidationError(
                        "Time channels " +
                        "CANNOT have any markers")
                if value_type != 'T':
                    raise ValidationError(
                        "Time channels " +
                        "must have a T value type")

            # make a list of the combination for use in the Counter
            # but, unstained params aren't required to be unique
            if param_type not in ['UNS', 'NUL']:
                param_components = [param_type, value_type]
                if fluorochrome_id:
                    param_components.append(fluorochrome_id)

                param_counter.update([tuple(sorted(param_components))])

            fcs_number = form.data[form.add_prefix('fcs_number')]
            param_dict[fcs_number] = {
                'parameter_type': param_type,
                'parameter_value_type': value_type,
                'fluorochrome_id': fluorochrome_id,
                'marker_id_set': marker_set
            }

        # check for duplicate parameters
        if max(param_counter.values()) > 1:
            raise ValidationError("Cannot have duplicate parameters")

        # Finally, check that all the project parameters are accounted for
        project_panel_parameters = \
            self.instance.project_panel.projectpanelparameter_set.all()
        matching_ids = []
        for ppp in project_panel_parameters:
            # first look for parameter type matches
            for d in param_dict:
                if ppp.parameter_type != param_dict[d]['parameter_type']:
                    # no match
                    continue

                if ppp.parameter_value_type:
                    if ppp.parameter_value_type != param_dict[d]['parameter_value_type']:
                        # no match
                        continue

                if ppp.fluorochrome_id:
                    if str(ppp.fluorochrome_id) != param_dict[d]['fluorochrome_id']:
                        # no match
                        continue

                if ppp.projectpanelparametermarker_set.count() > 0:
                    if ppp.projectpanelparametermarker_set.count() != len(param_dict[d]['marker_id_set']):
                        # no match
                        continue

                    should_continue = False
                    for ppp_marker in ppp.projectpanelparametermarker_set.all():
                        if ppp_marker.marker.id not in param_dict[d]['marker_id_set']:
                            # no match
                            should_continue = True
                            break
                    if should_continue:
                        continue
                # if we get here where are we?
                matching_ids.append(ppp.id)
                break

        # At the end there should be no project parameters on our list,
        # they all must be implemented by the site panel
        project_panel_parameters = project_panel_parameters.exclude(
            id__in=matching_ids)
        for ppp in project_panel_parameters:
            raise ValidationError(
                "Project parameter id %d was not used" % ppp.id)


class ProjectPanelForm(forms.ModelForm):
    class Meta:
        model = ProjectPanel
        exclude = ('project',)  # don't allow changing the parent project

    def __init__(self, *args, **kwargs):
        # pop our 'project_id' key since parent's init is not expecting it
        project_id = kwargs.pop('project_id', None)

        # now it's safe to call the parent init
        super(ProjectPanelForm, self).__init__(*args, **kwargs)

        # finally, make sure only project's subject groups are the
        # available choices, and that the only panels shown are Full stain
        if project_id:
            parent_panels = ProjectPanel.objects.filter(
                project__id=project_id,
                staining="FS")
            self.fields['parent_panel'] = forms.ModelChoiceField(
                parent_panels,
                required=False)

    def clean(self):
        # check for any site panel's made from this project panel
        # don't allow editing a project panel if any are found
        if self.instance:
            if self.instance.sitepanel_set.count() > 0:
                raise ValidationError(
                    "This panel cannot be edited because one or more site " +
                    "panels built from this project panel exist.")

        staining = self.cleaned_data.get('staining')
        parent_panel = self.cleaned_data.get('parent_panel')

        if not staining:
            return self.cleaned_data

        if staining == 'FS' and parent_panel:
            raise ValidationError(
                "Full stain panels cannot have parent panels.")
        if staining == 'FM':
            if not parent_panel:
                raise ValidationError(
                    "FMO panels require a parent full stain panel")
            elif parent_panel.staining != 'FS':
                raise ValidationError(
                    "FMO panels require a parent full stain panel")
        elif staining == 'IS':
            if not parent_panel:
                raise ValidationError(
                    "Isotype control panels require a parent full stain panel")
            elif parent_panel.staining != 'FS':
                raise ValidationError(
                    "Isotype control panels require a parent full stain panel")
        return self.cleaned_data


ProjectPanelParameterMarkerFormSet = inlineformset_factory(
    ProjectPanelParameter,
    ProjectPanelParameterMarker,
    extra=1,
    can_delete=True)


SitePanelParameterMarkerFormSet = inlineformset_factory(
    SitePanelParameter,
    SitePanelParameterMarker,
    extra=1,
    can_delete=False)


ProjectParameterFormSet = inlineformset_factory(
    ProjectPanel,
    ProjectPanelParameter,
    formset=BaseProjectPanelParameterFormSet,
    extra=1,
    can_delete=False
)

ProjectParameterFormSetEdit = inlineformset_factory(
    ProjectPanel,
    ProjectPanelParameter,
    formset=BaseProjectPanelParameterFormSet,
    extra=0,
    can_delete=True
)