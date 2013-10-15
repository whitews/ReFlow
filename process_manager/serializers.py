from rest_framework import serializers

from process_manager.models import *


class ProcessSerializer(serializers.ModelSerializer):
    #url = serializers.HyperlinkedIdentityField(view_name='process-detail')

    class Meta:
        model = Process
        fields = ('id', 'process_name', 'process_description')


class WorkerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Worker
        fields = ('id', 'worker_name', 'worker_version', 'worker_hostname')


class ProcessRequestSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='process-request-detail')

    class Meta:
        model = ProcessRequest
        fields = (
            'id',
            'url',
            'process',
            'sample_set',
            'worker',
            'request_user',
            'request_date',
            'status',
            'completion_date')


class ProcessRequestInputValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessRequestInputValue
        fields = ('id', 'process_input', 'value')
        depth = 1


class ProcessRequestDetailSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='process-request-detail')
    input_values = ProcessRequestInputValueSerializer(
        source='processrequestinputvalue_set')

    class Meta:
        model = ProcessRequest
        fields = (
            'id',
            'url',
            'process',
            'sample_set',
            'worker',
            'request_user',
            'request_date',
            'status',
            'completion_date',
            'input_values')