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

    class Meta:
        model = Subject
        fields = ('id', 'url', 'subject_code', 'subject_group', 'project',)


class SpecimenSerializer(serializers.ModelSerializer):

    class Meta:
        model = Specimen


class ProjectPanelParameterAntibodySerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        source='antibody.antibody_abbreviation',
        read_only=True)

    class Meta:
        model = ProjectPanelParameterAntibody
        exclude = ('id', 'parameter', 'antibody')


class ProjectPanelParameterSerializer(serializers.ModelSerializer):
    antibodies = ProjectPanelParameterAntibodySerializer(
        source='projectpanelparameterantibody_set')
    url = serializers.HyperlinkedIdentityField(view_name='project-parameter-detail')

    class Meta:
        model = ProjectPanelParameter
        fields = (
            'id',
            'url',
            'parameter_type',
            'parameter_value_type',
            'antibodies',
            'fluorochrome')


class ProjectPanelSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='project-panel-detail')
    parameters = ProjectPanelParameterSerializer(
        source='projectpanelparameter_set')

    class Meta:
        model = ProjectPanel
        fields = (
            'id',
            'url',
            'project',
            'panel_name',
            'staining',
            'parent_panel',
            'parameters'
        )


class SitePanelParameterAntibodySerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        source='antibody.antibody_abbreviation',
        read_only=True)

    class Meta:
        model = SitePanelParameterAntibody
        exclude = ('id', 'parameter', 'antibody')


class SitePanelParameterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='name', read_only=True)
    antibodies = SitePanelParameterAntibodySerializer(
        source='sitepanelparameterantibody_set')

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
            'antibodies',
            'fluorochrome')
        depth = 1


class SitePanelSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(source='site.project')
    site = SiteSerializer(source='site')
    parameters = SitePanelParameterSerializer(source='sitepanelparameter_set')
    url = serializers.HyperlinkedIdentityField(view_name='site-panel-detail')

    class Meta:
        model = SitePanel
        fields = (
            'id',
            'url',
            'project',
            'site',
            'project_panel',
            'parameters')


class StimulationSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='stimulation-detail')

    class Meta:
        model = Stimulation


class CompensationSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='compensation-detail')

    class Meta:
        model = Compensation
        fields = ('id', 'url', 'original_filename', 'matrix_text', 'site')
        exclude = ('compensation_file',)


class SampleSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='sample-detail')
    project = serializers.IntegerField(
        source='subject.project_id',
        read_only=True)
    subject_code = serializers.CharField(
        source='subject.subject_code',
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

    class Meta:
        model = Sample
        fields = (
            'id',
            'url',
            'visit',
            'visit_name',
            'subject',
            'subject_code',
            'specimen',
            'specimen_name',
            'stimulation',
            'stimulation_name',
            'project_panel',
            'panel_name',
            'site_panel',
            'site_name',
            'project',
            'original_filename',
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
        read_only_fields = ('original_filename', 'sha1')


class SampleSetListSerializer(serializers.ModelSerializer):
    """
    Display the list of sample sets (without related samples)
    """
    url = serializers.HyperlinkedIdentityField(view_name='sample-set-detail')

    class Meta:
        model = SampleSet
        fields = ('id', 'url', 'name', 'description', 'project')


class SampleSetSerializer(serializers.ModelSerializer):
    samples = SampleSerializer(source='samples')
    url = serializers.HyperlinkedIdentityField(view_name='sample-set-detail')

    class Meta:
        model = SampleSet
        fields = ('id', 'url', 'name', 'description', 'project', 'samples')