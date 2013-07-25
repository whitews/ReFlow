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

    class Meta:
        model = ProcessRequest
        fields = ('id', 'process', 'worker', 'request_user', 'request_date', 'status', 'completion_date')