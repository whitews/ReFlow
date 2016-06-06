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
        extra_kwargs = {
            'password': {'write_only': True}
        }


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
    sample_count = serializers.IntegerField(
        source='get_sample_count',
        read_only=True
    )
    compensation_count = serializers.IntegerField(
        source='get_compensation_count',
        read_only=True
    )

    class Meta:
        model = Project


class UsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)


class ProjectUserSerializer(serializers.ModelSerializer):
    users = UsernameSerializer(source='get_project_users', many=True)

    class Meta:
        model = Project
        fields = ('id', 'users')


class CellSubsetLabelSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='cell-subset-label-detail'
    )

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


class SiteSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='site-detail')
    sample_count = serializers.IntegerField(
        source='get_sample_count',
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
            'project',
            'sample_count',
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
        exclude = ('panel_template_parameter', 'marker')


class PanelTemplateParameterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    markers = PanelTemplateParameterMarkerSerializer(
        source='paneltemplateparametermarker_set',
        many=True
    )
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


class PanelVariantSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='panel-variant-detail'
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
        model = PanelVariant
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
    panel_variants = PanelVariantSerializer(
        source='panelvariant_set',
        many=True
    )
    parameters = PanelTemplateParameterSerializer(
        source='paneltemplateparameter_set',
        many=True
    )
    site_panel_count = serializers.IntegerField(
        source='sitepanel_set.count',
        read_only=True
    )
    sample_count = serializers.IntegerField(
        source='get_sample_count',
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
            'panel_variants',
            'parameters',
            'site_panel_count',
            'sample_count',
            'compensation_count'
        )


class SitePanelParameterMarkerSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        source='marker.marker_abbreviation',
        read_only=True)

    class Meta:
        model = SitePanelParameterMarker
        exclude = ('id', 'site_panel_parameter', 'marker')


class SitePanelParameterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    parameter_type_name = serializers.CharField(
        source="get_parameter_type_display",
        read_only=True
    )
    markers = SitePanelParameterMarkerSerializer(
        source='sitepanelparametermarker_set',
        many=True
    )

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
        many=True,
        read_only=True
    )
    url = serializers.HyperlinkedIdentityField(view_name='site-panel-detail')
    name = serializers.CharField(read_only=True)
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
            'compensation_count',
            'panel_template',
            'site_name',
            'implementation',
            'site_panel_comments',
            'panel_template_name',
            'name',
            'parameters'
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
    compensation_file = serializers.FileField(read_only=True)

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


class SampleSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='sample-detail')
    project = serializers.IntegerField(
        source='subject.project_id',
        read_only=True)
    project_name = serializers.CharField(
        source='subject.project.project_name',
        read_only=True)
    subject_group_name = serializers.CharField(
        source='subject.subject_group.group_name',
        read_only=True
    )
    subject_code = serializers.CharField(
        source='subject.subject_code',
        read_only=True)
    site = serializers.IntegerField(
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
        format='%Y-%m-%d %H:%M:%S',
        read_only=True)
    has_compensation = serializers.BooleanField(
        read_only=True
    )

    class Meta:
        model = Sample
        fields = (
            'id',
            'url',
            'visit',
            'visit_name',
            'acquisition_date',
            'upload_date',
            'subject_group_name',
            'subject',
            'subject_code',
            'specimen',
            'specimen_name',
            'storage',
            'pretreatment',
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
            'has_compensation',
            'sha1',
        )
        read_only_fields = (
            'original_filename', 'sha1', 'site_panel'
        )


class SamplePOSTSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='sample-detail')

    class Meta:
        model = Sample
        fields = (
            'id', 'url', 'visit', 'subject', 'specimen',
            'stimulation', 'panel_variant', 'site_panel',
            'original_filename', 'acquisition_date', 'sample_file'
        )
        read_only_fields = ('original_filename', 'sha1')


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
        source='samplecollectionmember_set',
        required=False,
        many=True
    )

    class Meta:
        model = SampleCollection
        fields = ('id', 'project', 'members')


class SampleCollectionDetailSerializer(serializers.ModelSerializer):
    members = SampleCollectionMemberDetailSerializer(
        source='samplecollectionmember_set',
        many=True,
        required=False
    )

    class Meta:
        model = SampleCollection
        fields = ('id', 'project', 'members')


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


class ProcessRequestStage2ClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessRequestStage2Cluster
        fields = ('process_request', 'cluster')


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
    parent_description = serializers.CharField(
        source='parent_stage.description',
        read_only=True
    )

    class Meta:
        model = ProcessRequest
        fields = (
            'id',
            'url',
            'project',
            'parent_stage',
            'parent_description',
            'sample_collection',
            'subsample_count',
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
            'status_message',
            'percent_complete'
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
        source='processrequestinput_set',
        many=True
    )
    stage2_clusters = ProcessRequestStage2ClusterSerializer(
        source='processrequeststage2cluster_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = ProcessRequest
        fields = (
            'id',
            'url',
            'project',
            'parent_stage',
            'stage2_clusters',
            'sample_collection',
            'subsample_count',
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
            'status_message',
            'percent_complete',
            'inputs'
        )


class ProcessRequestProgessDetailSerializer(serializers.ModelSerializer):
    worker_name = serializers.CharField(
        source='worker.worker_name',
        read_only=True
    )

    class Meta:
        model = ProcessRequest
        fields = (
            'status',
            'status_message',
            'worker_name',
            'assignment_date',
            'percent_complete'
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
    name = serializers.CharField(
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
            'name'
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


class SampleClusterSerializer(serializers.ModelSerializer):
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
        many=True,
        read_only=True
    )
    labels = ClusterLabelSerializer(
        source='cluster.clusterlabel_set',
        read_only=True,
        many=True
    )
    weight = serializers.CharField(read_only=True)

    class Meta:
        model = SampleCluster
        fields = (
            'id',
            'process_request',
            'sample',
            'cluster',
            'cluster_index',
            'parameters',
            'labels',
            'weight'
        )


class SampleClusterComponentParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleClusterComponentParameter
        fields = (
            'id',
            'sample_cluster_component',
            'channel',
            'location'
        )


class SampleClusterComponentSerializer(serializers.ModelSerializer):
    process_request = serializers.CharField(
        source='sample_cluster.cluster.process_request_id',
        read_only=True
    )
    sample = serializers.CharField(
        source='sample_cluster.sample_id',
        read_only=True
    )
    cluster = serializers.CharField(
        source='sample_cluster.cluster_id',
        read_only=True
    )
    parameters = SampleClusterComponentParameterSerializer(
        source='sampleclustercomponentparameter_set',
        many=True,
        read_only=True
    )
    labels = serializers.PrimaryKeyRelatedField(
        source='sample_cluster.cluster.clusterlabel_set',
        read_only=True,
        many=True
    )
    weight = serializers.CharField(read_only=True)

    class Meta:
        model = SampleClusterComponent
        fields = (
            'id',
            'process_request',
            'sample',
            'cluster',
            'covariance_matrix',
            'weight',
            'parameters',
            'labels'
        )
