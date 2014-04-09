from rest_framework import serializers

from repository.models import *


class ProjectSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='project-detail')

    class Meta:
        model = Project
        fields = ('id', 'url', 'project_name', 'project_desc')


class VisitTypeSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='visittype-detail')

    class Meta:
        model = VisitType
        fields = (
            'id',
            'url',
            'visit_type_name',
            'visit_type_description',
            'project')


class SubjectGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectGroup


class SiteSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(source='project')
    url = serializers.HyperlinkedIdentityField(view_name='site-detail')

    class Meta:
        model = Site
        fields = ('id', 'url', 'site_name', 'project')


class SubjectSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(source='project')
    url = serializers.HyperlinkedIdentityField(view_name='subject-detail')
    subject_group_name = serializers.CharField(
        source='subject_group.group_name',
        read_only=True)

    class Meta:
        model = Subject
        fields = (
            'id',
            'url',
            'subject_code',
            'subject_group',
            'subject_group_name',
            'batch_control',
            'project',)


class MarkerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Marker


class SpecimenSerializer(serializers.ModelSerializer):

    class Meta:
        model = Specimen


class ProjectPanelParameterMarkerSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        source='marker.marker_abbreviation',
        read_only=True)

    class Meta:
        model = ProjectPanelParameterMarker
        exclude = ('parameter', 'marker')


class ProjectPanelParameterSerializer(serializers.ModelSerializer):
    markers = ProjectPanelParameterMarkerSerializer(
        source='projectpanelparametermarker_set')
    fluorochrome_abbreviation = serializers.CharField(
        source="fluorochrome.fluorochrome_abbreviation",
        read_only=True)

    class Meta:
        model = ProjectPanelParameter
        fields = (
            'id',
            'parameter_type',
            'parameter_value_type',
            'markers',
            'fluorochrome',
            'fluorochrome_abbreviation')


class ProjectPanelSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='project-panel-detail')
    parameters = ProjectPanelParameterSerializer(
        source='projectpanelparameter_set')
    staining_name = serializers.CharField(
        source='get_staining_display',
        read_only=True)

    class Meta:
        model = ProjectPanel
        fields = (
            'id',
            'url',
            'project',
            'panel_name',
            'staining',
            'staining_name',
            'parent_panel',
            'parameters'
        )


class SitePanelParameterMarkerSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        source='marker.marker_abbreviation',
        read_only=True)

    class Meta:
        model = SitePanelParameterMarker
        exclude = ('id', 'parameter', 'marker')


class SitePanelParameterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='name', read_only=True)
    markers = SitePanelParameterMarkerSerializer(
        source='sitepanelparametermarker_set')

    class Meta:
        model = SitePanelParameter
        fields = (
            'id',
            'fcs_number',
            'fcs_text',
            'fcs_opt_text',
            'name',
            'parameter_type',
            'parameter_value_type',
            'markers',
            'fluorochrome')
        depth = 1


class SitePanelSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(source='site.project')
    site = SiteSerializer(source='site')
    parameters = SitePanelParameterSerializer(source='sitepanelparameter_set')
    url = serializers.HyperlinkedIdentityField(view_name='site-panel-detail')
    name = serializers.CharField(source='name')
    project_panel_name = serializers.CharField(
        source='project_panel.panel_name')

    class Meta:
        model = SitePanel
        fields = (
            'id',
            'url',
            'project',
            'site',
            'project_panel',
            'project_panel_name',
            'name',
            'parameters')


class CytometerSerializer(serializers.ModelSerializer):
    site = SiteSerializer(source='site')
    site_name = serializers.CharField(source='site.site_name')
    url = serializers.HyperlinkedIdentityField(view_name='cytometer-detail')

    class Meta:
        model = Cytometer
        fields = (
            'id',
            'url',
            'site',
            'site_name',
            'cytometer_name',
            'serial_number')


class StimulationSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='stimulation-detail')

    class Meta:
        model = Stimulation


class CompensationSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='compensation-detail')
    project = ProjectSerializer(
        source='site_panel.site.project',
        read_only=True)
    site = SiteSerializer(source='site_panel.site', read_only=True)
    compensation_file = serializers.FileField(
        source='compensation_file',
        read_only=True)

    class Meta:
        model = Compensation
        fields = (
            'id',
            'url',
            'name',
            'matrix_text',
            'project',
            'site',
            'site_panel',
            'acquisition_date',
            'compensation_file'
        )

    def validate(self, attrs):
        """
        Validate compensation matrix matches site panel and is, um, valid
        """
        if not 'site_panel' in attrs:
            # site panel is required, will get caught
            return attrs
        if not 'matrix_text' in attrs:
            # matrix text is required, will get caught
            return attrs

        try:
            site_panel = SitePanel.objects.get(
                id=attrs['site_panel'].id)
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
        matrix_text = str(attrs['matrix_text'])
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
            return attrs

        if len(headers) > params.count():
            self._errors["matrix_text"] = "Too many parameters"
            return attrs

        # the header of matrix text adds a row
        if len(matrix_text) > params.count() + 1:
            self._errors["matrix_text"] = "Too many rows"
            return attrs
        elif len(matrix_text) < params.count() + 1:
            self._errors["matrix_text"] = "Too few rows"
            return attrs

        # convert the matrix text to numpy array and
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
                return attrs
            elif len(line_values) < len(params):
                self._errors["matrix_text"] = \
                    "Too few values in line: %s" % line
                return attrs

        return attrs


class SampleSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='sample-detail')
    project = serializers.IntegerField(
        source='subject.project_id',
        read_only=True)
    subject_code = serializers.CharField(
        source='subject.subject_code',
        read_only=True)
    site = serializers.CharField(
        source='site_panel.site_id',
        read_only=True)
    site_name = serializers.CharField(
        source='site_panel.site.site_name',
        read_only=True)
    visit_name = serializers.CharField(
        source='visit.visit_type_name',
        read_only=True)
    specimen_name = serializers.CharField(
        source='specimen.specimen_name',
        read_only=True)
    stimulation_name = serializers.CharField(
        source='stimulation.stimulation_name',
        read_only=True)
    project_panel = serializers.IntegerField(
        source='site_panel.project_panel_id',
        read_only=True)
    panel_name = serializers.CharField(
        source='site_panel.project_panel.panel_name',
        read_only=True)
    upload_date = serializers.DateTimeField(
        source='upload_date',
        format='%Y-%m-%d %H:%M:%S',
        read_only=True)

    class Meta:
        model = Sample
        fields = (
            'id',
            'url',
            'visit',
            'visit_name',
            'acquisition_date',
            'upload_date',
            'subject',
            'subject_code',
            'specimen',
            'specimen_name',
            'storage',
            'pretreatment',
            'cytometer',
            'stimulation',
            'stimulation_name',
            'project_panel',
            'panel_name',
            'site_panel',
            'site',
            'site_name',
            'project',
            'original_filename',
            'exclude',
            'sha1',
            'compensation'
        )
        read_only_fields = ('original_filename', 'sha1')
        exclude = ('sample_file',)


class SamplePOSTSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='sample-detail')
    project = serializers.IntegerField(
        source='subject.subject_group.project_id',
        read_only=True)

    def get_fields(self):
        fields = super(SamplePOSTSerializer, self).get_default_fields()
        user = self.context['view'].request.user
        user_projects = Project.objects.get_projects_user_can_view(user)
        if 'subject' in fields:
            fields['subject'].queryset = Subject.objects.filter(
                project__in=user_projects)
        if 'site' in fields:
            fields['site'].queryset = Site.objects.filter(
                project__in=user_projects)
        if 'visit' in fields:
            fields['visit'].queryset = VisitType.objects.filter(
                project__in=user_projects)

        return fields

    class Meta:
        model = Sample
        fields = (
            'id', 'url', 'visit', 'subject', 'specimen',
            'site_panel', 'project', 'original_filename',
            'sample_file'
        )
        read_only_fields = ('original_filename', 'sha1', 'subsample')
        exclude = ('subsample',)


class SampleMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleMetadata
        fields = ('id', 'sample', 'key', 'value')


class SampleCollectionMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleCollectionMember
        fields = ('id', 'sample_collection', 'sample')


class SampleCollectionMemberDetailSerializer(serializers.ModelSerializer):
    sample = SampleSerializer()

    class Meta:
        model = SampleCollectionMember
        fields = ('id', 'sample_collection', 'sample')


class SampleCollectionSerializer(serializers.ModelSerializer):
    members = SampleCollectionMemberSerializer(
        source='samplecollectionmember_set', required=False)

    class Meta:
        model = SampleCollection
        fields = ('id', 'project', 'members')


class SampleCollectionDetailSerializer(serializers.ModelSerializer):
    members = SampleCollectionMemberDetailSerializer(
        source='samplecollectionmember_set', required=False)

    class Meta:
        model = SampleCollection
        fields = ('id', 'project', 'members')


class WorkerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Worker
        fields = ('id', 'worker_name', 'worker_hostname')


class SubprocessCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubprocessCategory
        fields = (
            'id',
            'name',
            'description'
        )


class SubprocessImplementationSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source='category.name',
        read_only=True)

    class Meta:
        model = SubprocessImplementation
        fields = (
            'id',
            'category',
            'category_name',
            'name',
            'description'
        )


class SubprocessInputSerializer(serializers.ModelSerializer):
    category = serializers.IntegerField(
        source='implementation.category_id',
        read_only=True)
    category_name = serializers.CharField(
        source='implementation.category.name',
        read_only=True)
    implementation_name = serializers.CharField(
        source='implementation.name',
        read_only=True)

    class Meta:
        model = SubprocessInput
        fields = (
            'id',
            'category',
            'category_name',
            'implementation',
            'implementation_name',
            'name',
            'description',
            'value_type',
            'required',
            'allow_multiple',
            'default'
        )


class ProcessRequestSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='process-request-detail')

    class Meta:
        model = ProcessRequest
        fields = (
            'id',
            'url',
            'project',
            'sample_collection',
            'description',
            'predefined',
            'request_user',
            'request_date',
            'assignment_date',
            'completion_date',
            'worker',
            'status'
        )


class ProcessRequestInputSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source='subprocess_input.implementation.category.name',
        read_only=True
    )
    implementation_name = serializers.CharField(
        source='subprocess_input.implementation.name',
        read_only=True
    )
    input_name = serializers.CharField(
        source='subprocess_input.name',
        read_only=True
    )
    value_type = serializers.CharField(
        source='subprocess_input.value_type',
        read_only=True
    )

    class Meta:
        model = ProcessRequestInput
        fields = (
            'id',
            'process_request',
            'subprocess_input',
            'category_name',
            'implementation_name',
            'input_name',
            'value_type',
            'value'
        )


class ProcessRequestOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessRequestOutput
        fields = (
            'id',
            'process_request',
            'key',
            'value'
        )


class ProcessRequestDetailSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='process-request-detail')
    inputs = ProcessRequestInputSerializer(
        source='processrequestinput_set')
    outputs = ProcessRequestOutputSerializer(
        source='processrequestoutput_set')

    class Meta:
        model = ProcessRequest
        fields = (
            'id',
            'url',
            'project',
            'sample_collection',
            'description',
            'predefined',
            'request_user',
            'request_date',
            'assignment_date',
            'completion_date',
            'worker',
            'status',
            'inputs',
            'outputs'
        )