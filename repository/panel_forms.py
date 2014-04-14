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


class EditSitePanelForm(forms.ModelForm):
    class Meta:
        model = SitePanel
        exclude = ('project_panel',)


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