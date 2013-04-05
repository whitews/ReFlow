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
        model = ProjectVisitType
        fields = ('id', 'url', 'visit_type_name', 'visit_type_description', 'project')


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
        fields = ('id', 'url', 'subject_id', 'project')


class ParameterAntibodySerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='antibody.antibody_short_name', read_only=True)

    class Meta:
        model = ParameterAntibodyMap
        exclude = ('id', 'parameter', 'antibody')


class ParameterFluorochromeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='fluorochrome.fluorochrome_short_name', read_only=True)

    class Meta:
        model = ParameterFluorochromeMap
        exclude = ('id', 'parameter', 'antibody')


class ParameterSerializer(serializers.ModelSerializer):
    antibodies = ParameterAntibodySerializer(source='parameterantibodymap_set')
    fluorochromes = ParameterFluorochromeSerializer(source='parameterfluorochromemap_set')
    url = serializers.HyperlinkedIdentityField(view_name='parameter-detail')

    class Meta:
        model = Parameter
        fields = ('id', 'url', 'parameter_short_name', 'parameter_type', 'antibodies', 'fluorochromes')


class PanelParameterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='name', read_only=True)

    class Meta:
        model = PanelParameterMap
        fields = ('id', 'fcs_text', 'name')
        depth = 1


class PanelSerializer(serializers.ModelSerializer):
    site = SiteSerializer(source='site')
    panelparameters = PanelParameterSerializer(source='panelparametermap_set')
    url = serializers.HyperlinkedIdentityField(view_name='panel-detail')

    class Meta:
        model = Panel
        fields = ('id', 'url', 'panel_name', 'site', 'panelparameters')


class SampleParameterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='name', read_only=True)

    class Meta:
        model = SampleParameterMap
        fields = ('id', 'fcs_text', 'fcs_opt_text', 'fcs_number', 'name')
        depth = 1


class CompensationSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='compensation-detail')

    class Meta:
        model = Compensation
        fields = ('id', 'url', 'original_filename', 'matrix_text', 'site')
        exclude = ('compensation_file',)


class SampleCompensationSerializer(serializers.ModelSerializer):
    compensation = CompensationSerializer(source='compensation')

    class Meta:
        model = SampleCompensationMap
        fields = ('id', 'compensation',)
        depth = 1


class SampleCompensationPOSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleCompensationMap

    def get_fields(self):
        fields = super(SampleCompensationPOSTSerializer, self).get_default_fields()
        user = self.context['view'].request.user
        user_projects = Project.objects.get_projects_user_can_view(user)
        if 'compensation' in fields:
            fields['compensation'].queryset = Compensation.objects.filter(site__project__in=user_projects)
        if 'sample' in fields:
            fields['sample'].queryset = Sample.objects.filter(subject__project__in=user_projects)

        return fields


class SampleSerializer(serializers.ModelSerializer):
    sampleparameters = SampleParameterSerializer(source='sampleparametermap_set')
    compensations = SampleCompensationSerializer(source='samplecompensationmap_set')
    url = serializers.HyperlinkedIdentityField(view_name='sample-detail')
    project = serializers.IntegerField(source='subject.project_id', read_only=True)

    class Meta:
        model = Sample
        fields = (
            'id',
            'url',
            'visit',
            'subject',
            'site',
            'project',
            'original_filename',
            'sha1',
            'sampleparameters',
            'compensations'
        )
        read_only_fields = ('original_filename', 'sha1')
        exclude = ('sample_file',)


class SamplePOSTSerializer(serializers.ModelSerializer):
    sampleparameters = SampleParameterSerializer(source='sampleparametermap_set')
    url = serializers.HyperlinkedIdentityField(view_name='sample-detail')
    project = serializers.IntegerField(source='subject.project_id', read_only=True)

    def get_fields(self):
        fields = super(SamplePOSTSerializer, self).get_default_fields()
        user = self.context['view'].request.user
        user_projects = Project.objects.get_projects_user_can_view(user)
        if 'subject' in fields:
            fields['subject'].queryset = Subject.objects.filter(project__in=user_projects)
        if 'site' in fields:
            fields['site'].queryset = Site.objects.filter(project__in=user_projects)
        if 'visit' in fields:
            fields['visit'].queryset = ProjectVisitType.objects.filter(project__in=user_projects)

        return fields

    class Meta:
        model = Sample
        fields = (
            'id', 'url', 'visit', 'subject',
            'site', 'project', 'original_filename',
            'sampleparameters', 'sample_file'
        )
        read_only_fields = ('original_filename', 'sha1')
