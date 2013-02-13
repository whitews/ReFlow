from repository.models import *
from rest_framework import serializers

class ProjectSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='project-detail')

    class Meta:
        model = Project
        fields = ('id', 'project_name', 'project_desc', 'url')

class SampleParameterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='name', read_only=True)

    class Meta:
        model = SampleParameterMap
        fields = ('id', 'fcs_text', 'fcs_number', 'name')
        depth = 1

class SampleSerializer(serializers.ModelSerializer):
    sampleparameters = SampleParameterSerializer(source='sampleparametermap_set')

    class Meta:
        model = Sample
        fields = ('id', 'subject', 'original_filename', 'sampleparameters')


