from rest_framework import serializers

from repository.models import *
from django.contrib.auth.models import User
from guardian.models import UserObjectPermission


class PermissionSerializer(serializers.ModelSerializer):
    model = serializers.CharField(source='content_type.model')
    username = serializers.CharField(source='user.username')
    permission_codename = serializers.CharField(source='permission.codename')
    permission_name = serializers.CharField(
        source='permission.name',
        read_only=True
    )

    class Meta:
        model = UserObjectPermission
        fields = (
            'id',
            'model',
            'object_pk',
            'username',
            'permission',
            'permission_codename',
            'permission_name'
        )
        read_only_fields = ('permission',)


class UserSerializer(serializers.ModelSerializer):
    process_request_count = serializers.IntegerField(
        source='processrequest_set.count',
        read_only=True
    )

    class Meta:
        model = User
        exclude = ('password',)


class ProjectSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='project-detail')
    subject_count = serializers.IntegerField(
        source='subject_set.count',
        read_only=True
    )
    visit_type_count = serializers.IntegerField(
        source='visittype_set.count',
        read_only=True
    )
    panel_count = serializers.IntegerField(
        source='paneltemplate_set.count',
        read_only=True
    )
    site_count = serializers.IntegerField(
        source='site_set.count',
        read_only=True
    )
    cytometer_count = serializers.IntegerField(
        source='get_sample_count',
        read_only=True
    )
    sample_count = serializers.IntegerField(
        source='get_sample_count',
        read_only=True
    )
    bead_sample_count = serializers.IntegerField(
        source='get_bead_sample_count',
        read_only=True
    )
    compensation_count = serializers.IntegerField(
        source='get_compensation_count',
        read_only=True
    )

    class Meta:
        model = Project


class ProjectUserSerializer(serializers.ModelSerializer):
    users = serializers.Field(source='get_project_users')

    class Meta:
        model = User
        fields = ('id', 'users')


class CellSubsetLabelSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='cell-subset-label-detail')

    class Meta:
        model = CellSubsetLabel


class VisitTypeSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='visittype-detail')
    sample_count = serializers.IntegerField(
        source='sample_set.count',
        read_only=True
    )

    class Meta:
        model = VisitType
        fields = (
            'id',
            'url',
            'visit_type_name',
            'visit_type_description',
            'project',
            'sample_count'
        )


class SubjectGroupSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='subject-group-detail')
    subject_count = serializers.IntegerField(
        source='subject_set.count',
        read_only=True
    )
    sample_count = serializers.IntegerField(
        source='get_sample_count',
        read_only=True
    )

    class Meta:
        model = SubjectGroup


class CytometerFlatSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='cytometer-detail')

    class Meta:
        model = Cytometer
        fields = (
            'id',
            'url',
            'cytometer_name',
            'serial_number'
        )


class SiteSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='site-detail')
    cytometers = CytometerFlatSerializer(source='cytometer_set', read_only=True)
    cytometer_count = serializers.IntegerField(
        source='cytometer_set.count',
        read_only=True
    )
    sample_count = serializers.IntegerField(
        source='get_sample_count',
        read_only=True
    )
    bead_sample_count = serializers.IntegerField(
        source='get_bead_sample_count',
        read_only=True
    )
    compensation_count = serializers.IntegerField(
        source='get_compensation_count',
        read_only=True
    )

    class Meta:
        model = Site
        fields = (
            'id',
            'url',
            'site_name',
            'cytometers',
            'project',
            'cytometer_count',
            'sample_count',
            'bead_sample_count',
            'compensation_count'
        )


class SubjectSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='subject-detail')
    subject_group_name = serializers.CharField(
        source='subject_group.group_name',
        read_only=True)
    sample_count = serializers.IntegerField(
        source='sample_set.count',
        read_only=True
    )

    class Meta:
        model = Subject
        fields = (
            'id',
            'url',
            'subject_code',
            'subject_group',
            'subject_group_name',
            'batch_control',
            'project',
            'sample_count'
        )


class MarkerSerializer(serializers.ModelSerializer):
    parameter_count = serializers.IntegerField(
        source='sitepanelparametermarker_set.count',
        read_only=True
    )

    class Meta:
        model = Marker


class FluorochromeSerializer(serializers.ModelSerializer):
    parameter_count = serializers.IntegerField(
        source='sitepanelparameter_set.count',
        read_only=True
    )

    class Meta:
        model = Fluorochrome


class SpecimenSerializer(serializers.ModelSerializer):
    sample_count = serializers.IntegerField(
        source='sample_set.count',
        read_only=True
    )

    class Meta:
        model = Specimen


class PanelTemplateParameterMarkerSerializer(serializers.ModelSerializer):
    marker_id = serializers.CharField(
        source='marker.id',
        read_only=True)
    name = serializers.CharField(
        source='marker.marker_abbreviation',
        read_only=True)

    class Meta:
        model = PanelTemplateParameterMarker
        exclude = ('parameter', 'marker')


class PanelTemplateParameterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='name', read_only=True)
    markers = PanelTemplateParameterMarkerSerializer(
        source='paneltemplateparametermarker_set')
    fluorochrome_abbreviation = serializers.CharField(
        source="fluorochrome.fluorochrome_abbreviation",
        read_only=True)
    parameter_type_name = serializers.CharField(
        source="get_parameter_type_display",
        read_only=True
    )

    class Meta:
        model = PanelTemplateParameter
        fields = (
            'id',
            'name',
            'parameter_type',
            'parameter_type_name',
            'parameter_value_type',
            'markers',
            'fluorochrome',
            'fluorochrome_abbreviation')


class StainingClassSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='staining-class-detail'
    )
    staining_type_name = serializers.CharField(
        source="get_staining_type_display",
        read_only=True
    )
    sample_count = serializers.IntegerField(
        source='sample_set.count',
        read_only=True
    )

    class Meta:
        model = StainingClass
        fields = (
            'url',
            'id',
            'panel_template',
            'staining_type',
            'staining_type_name',
            'name',
            'sample_count'
        )


class PanelTemplateSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='panel-template-detail'
    )
    staining_classes = StainingClassSerializer(
        source='stainingclass_set'
    )
    parameters = PanelTemplateParameterSerializer(
        source='paneltemplateparameter_set'
    )
    site_panel_count = serializers.IntegerField(
        source='sitepanel_set.count',
        read_only=True
    )
    sample_count = serializers.IntegerField(
        source='get_sample_count',
        read_only=True
    )
    bead_sample_count = serializers.IntegerField(
        source='get_bead_sample_count',
        read_only=True
    )
    compensation_count = serializers.IntegerField(
        source='get_compensation_count',
        read_only=True
    )

    class Meta:
        model = PanelTemplate
        fields = (
            'id',
            'url',
            'project',
            'panel_name',
            'panel_description',
            'staining_classes',
            'parameters',
            'site_panel_count',
            'sample_count',
            'bead_sample_count',
            'compensation_count'
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
    parameter_type_name = serializers.CharField(
        source="get_parameter_type_display",
        read_only=True
    )
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
            'parameter_type_name',
            'parameter_value_type',
            'markers',
            'fluorochrome')
        depth = 1


class SitePanelSerializer(serializers.ModelSerializer):
    project = serializers.IntegerField(
        source='site.project_id',
        read_only=True
    )
    project_name = serializers.CharField(
        source='site.project.project_name',
        read_only=True
    )
    parameters = SitePanelParameterSerializer(
        source='sitepanelparameter_set',
        read_only=True
    )
    url = serializers.HyperlinkedIdentityField(view_name='site-panel-detail')
    name = serializers.CharField(source='name', read_only=True)
    panel_template_name = serializers.CharField(
        source='panel_template.panel_name',
        read_only=True
    )
    site_name = serializers.CharField(
        source='site.site_name',
        read_only=True
    )
    sample_count = serializers.IntegerField(
        source='sample_set.count',
        read_only=True
    )
    bead_sample_count = serializers.IntegerField(
        source='beadsample_set.count',
        read_only=True
    )
    compensation_count = serializers.IntegerField(
        source='compensation_set.count',
        read_only=True
    )

    class Meta:
        model = SitePanel
        fields = (
            'id',
            'url',
            'project',
            'project_name',
            'site',
            'sample_count',
            'bead_sample_count',
            'compensation_count',
            'panel_template',
            'site_name',
            'implementation',
            'site_panel_comments',
            'panel_template_name',
            'name',
            'parameters'
        )


class CytometerSerializer(serializers.ModelSerializer):
    site_name = serializers.CharField(source='site.site_name', read_only=True)
    sample_count = serializers.IntegerField(
        source='sample_set.count',
        read_only=True
    )
    bead_sample_count = serializers.IntegerField(
        source='beadsample_set.count',
        read_only=True
    )
    url = serializers.HyperlinkedIdentityField(view_name='cytometer-detail')

    class Meta:
        model = Cytometer
        fields = (
            'id',
            'url',
            'site',
            'site_name',
            'cytometer_name',
            'serial_number',
            'sample_count',
            'bead_sample_count'
        )


class StimulationSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='stimulation-detail')
    sample_count = serializers.IntegerField(
        source='sample_set.count',
        read_only=True
    )

    class Meta:
        model = Stimulation


class CompensationSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='compensation-detail')
    project = serializers.IntegerField(
        source='site_panel.site.project_id',
        read_only=True
    )
    panel = serializers.IntegerField(
        source='site_panel.panel_template_id',
        read_only=True
    )
    panel_name = serializers.CharField(
        source='site_panel.panel_template.panel_name',
        read_only=True
    )
    site = serializers.IntegerField(source='site_panel.site_id', read_only=True)
    site_name = serializers.CharField(
        source='site_panel.site.site_name',
        read_only=True
    )
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
            'panel',
            'panel_name',
            'site',
            'site_name',
            'site_panel',
            'acquisition_date',
            'compensation_file',
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
    project_name = serializers.CharField(
        source='subject.project.project_name',
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
    panel = serializers.IntegerField(
        source='site_panel.panel_template_id',
        read_only=True)
    panel_name = serializers.CharField(
        source='site_panel.panel_template.panel_name',
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
            'panel',
            'panel_name',
            'site_panel',
            'site',
            'site_name',
            'project',
            'project_name',
            'original_filename',
            'exclude',
            'sha1',
        )
        read_only_fields = (
            'original_filename', 'sha1', 'site_panel', 'cytometer'
        )
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
    filename = serializers.CharField(
        source='sample.original_filename',
        read_only=True
    )

    class Meta:
        model = SampleCollectionMember
        fields = (
            'id',
            'sample_collection',
            'sample',
            'filename',
            'compensation'
        )


class SampleCollectionMemberDetailSerializer(serializers.ModelSerializer):
    sample = SampleSerializer()
    compensation = serializers.CharField(
        source='compensation.matrix_text',
        read_only=True
    )

    class Meta:
        model = SampleCollectionMember
        fields = ('id', 'sample_collection', 'sample', 'compensation')


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


class BeadSampleSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='bead-detail')
    project = serializers.IntegerField(
        source='site_panel.panel_template.project_id',
        read_only=True)
    site = serializers.CharField(
        source='site_panel.site_id',
        read_only=True)
    site_name = serializers.CharField(
        source='site_panel.site.site_name',
        read_only=True)
    panel_template = serializers.IntegerField(
        source='site_panel.panel_template_id',
        read_only=True)
    panel_name = serializers.CharField(
        source='site_panel.panel_template.panel_name',
        read_only=True)
    compensation_channel_name = serializers.CharField(
        source='compensation_channel.fluorochrome_abbreviation',
        read_only=True)
    upload_date = serializers.DateTimeField(
        source='upload_date',
        format='%Y-%m-%d %H:%M:%S',
        read_only=True)

    class Meta:
        model = BeadSample
        fields = (
            'id',
            'url',
            'acquisition_date',
            'upload_date',
            'cytometer',
            'panel_template',
            'panel_name',
            'site_panel',
            'compensation_channel',
            'compensation_channel_name',
            'site',
            'site_name',
            'project',
            'original_filename',
            'exclude',
            'sha1'
        )
        read_only_fields = ('original_filename', 'sha1')
        exclude = ('bead_file',)


class BeadSamplePOSTSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='bead-detail')
    project = serializers.IntegerField(
        source='site_panel.panel_template.project_id',
        read_only=True)

    def get_fields(self):
        fields = super(BeadSamplePOSTSerializer, self).get_default_fields()
        user = self.context['view'].request.user
        user_projects = Project.objects.get_projects_user_can_view(user)
        if 'site' in fields:
            fields['site'].queryset = Site.objects.filter(
                project__in=user_projects)

        return fields

    class Meta:
        model = BeadSample
        fields = (
            'id', 'url', 'site_panel', 'project', 'original_filename',
            'bead_file', 'compensation_channel'
        )
        read_only_fields = ('original_filename', 'sha1', 'subsample')
        exclude = ('subsample',)


class WorkerSerializer(serializers.ModelSerializer):
    process_request_count = serializers.IntegerField(
        source='processrequest_set.count',
        read_only=True
    )
    token = serializers.CharField(
        source='user.auth_token.key',
        read_only=True
    )

    class Meta:
        model = Worker
        exclude = ('user',)


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
    request_username = serializers.CharField(
        source='request_user.username',
        read_only=True
    )
    worker_name = serializers.CharField(
        source='worker.worker_name',
        read_only=True
    )

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
            'request_username',
            'request_date',
            'assignment_date',
            'completion_date',
            'worker',
            'worker_name',
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
        view_name='process-request-detail'
    )
    request_username = serializers.CharField(
        source='request_user.username',
        read_only=True
    )
    worker_name = serializers.CharField(
        source='worker.worker_name',
        read_only=True
    )
    inputs = ProcessRequestInputSerializer(
        source='processrequestinput_set'
    )
    outputs = ProcessRequestOutputSerializer(
        source='processrequestoutput_set'
    )

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
            'request_username',
            'request_date',
            'assignment_date',
            'completion_date',
            'worker',
            'worker_name',
            'status',
            'inputs',
            'outputs'
        )


class ClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cluster
        fields = (
            'id',
            'process_request',
            'index'
        )


class ClusterLabelSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='cluster-label-detail')
    process_request = serializers.IntegerField(
        source='cluster.process_request_id',
        read_only=True
    )
    cluster_index = serializers.IntegerField(
        source='cluster.index',
        read_only=True
    )
    label_name = serializers.CharField(
        source='label.name',
        read_only=True
    )

    class Meta:
        model = ClusterLabel
        fields = (
            'id',
            'url',
            'process_request',
            'cluster',
            'cluster_index',
            'label',
            'label_name'
        )


class SampleClusterParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleClusterParameter
        fields = (
            'id',
            'sample_cluster',
            'channel',
            'location'
        )


class EventClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventClassification
        fields = (
            'event_index',
        )


class SampleClusterSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(
    #     view_name='sample-cluster-detail'
    # )
    process_request = serializers.CharField(
        source='cluster.process_request_id',
        read_only=True
    )
    cluster_index = serializers.IntegerField(
        source='cluster.index',
        read_only=True
    )
    parameters = SampleClusterParameterSerializer(
        source='sampleclusterparameter_set',
        read_only=True
    )
    labels = serializers.RelatedField(
        source='cluster.clusterlabel_set',
        read_only=True,
        many=True
    )
    event_indices = serializers.RelatedField(
        source='eventclassification_set',
        read_only=True,
        many=True
    )

    class Meta:
        model = SampleCluster
        fields = (
            'id',
            #'url',
            'process_request',
            'sample',
            'cluster',
            'cluster_index',
            'parameters',
            'labels',
            'event_indices'
        )