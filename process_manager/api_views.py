from rest_framework import generics
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response

import django_filters

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from process_manager.models import *
from process_manager.serializers import *


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def process_manager_api_root(request, format=None):
    """
    The entry endpoint of our API.
    """

    return Response({
        'processes': reverse('process-list', request=request),
        'workers': reverse('worker-list', request=request),
        'process_requests': reverse('process-request-list', request=request),
        'viable_process_requests': reverse('viable-process-request-list', request=request),
    })


class LoginRequiredMixin(object):
    """
    View mixin to verify a user is logged in.
    """

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)


class PermissionRequiredMixin(object):
    """
    View mixin to verify a user is either a worker or superuser
    """

    def get_object(self, *args, **kwargs):
        if self.request.user.is_superuser or hasattr(self.request.user, 'worker'):
            return super(PermissionRequiredMixin, self).get_object(*args, **kwargs)
        else:
            return PermissionDenied


class ProcessList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of processes.
    """

    model = Process
    serializer_class = ProcessSerializer
    filter_fields = ('process_name',)


class WorkerList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of workers.
    """

    model = Worker
    serializer_class = WorkerSerializer
    filter_fields = ('worker_name',)


class ProcessRequestList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of process requests.
    """

    model = ProcessRequest
    serializer_class = ProcessRequestSerializer
    filter_fields = ('process', 'worker', 'request_user')


class ViableProcessRequestList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of process requests for which a Worker can request
    assignment.
    """

    model = ProcessRequest
    serializer_class = ProcessRequestSerializer
    filter_fields = ('process', 'worker', 'request_user')

    def get_queryset(self):
        """
        Override .get_queryset() to filter process requests to those with a 'Pending' status
        and those compatible with the calling worker. Regular users receive zero results.
        """

        if not hasattr(self.request.user, 'worker'):
            return ProcessRequest.objects.none()

        worker = Worker.objects.get(user=self.request.user)
        viable_process_id_list = worker.workerprocessmap_set.all().values_list('process_id', flat=True)

        # filter requests against these process IDs
        queryset = ProcessRequest.objects.filter(
            process_id__in=viable_process_id_list,
            status = 'Pending')
        return queryset


class ProcessRequestDetail(LoginRequiredMixin, PermissionRequiredMixin, generics.RetrieveAPIView):
    """
    API endpoint representing a single process request.
    """

    model = ProcessRequest
    serializer_class = ProcessRequestSerializer


class ProcessRequestAssignmentUpdate(LoginRequiredMixin, PermissionRequiredMixin, generics.UpdateAPIView):
    """
    API endpoint for requesting assignment for a ProcessRequest.
    """

    model = ProcessRequest
    serializer_class = ProcessRequest

    def patch(self, request, *args, **kwargs):
        """
        Override patch for validation:
          - ensure user is a Worker
          - Worker must be registered to the ProcessRequest's Process
          - ProcessRequest must not already be assigned
        """
        if hasattr(self.request.user, 'worker'):
            try:
                worker = Worker.objects.get(user=self.request.user)
                process_request = ProcessRequest.objects.get(id=kwargs['pk'])
            except Exception as e:
                return Response(data={'detail': e.message}, status=400)

            try:
                WorkerProcessMap.objects.get(worker=worker, process=process_request.process)
            except:
                raise PermissionDenied

            # check if ProcessRequest is already assigned
            if process_request.worker is not None:
                return Response(data={'detail': 'Request is already assigned'}, status=400)

            # if we get here, the worker is bonafide! "He's a suitor!"
            try:
                # now try to save the ProcessRequest
                process_request.worker = worker
                process_request.save()

                # serialize the updated ProcessRequest
                serializer = ProcessRequestSerializer(process_request)

                return Response(serializer.data, status=201)
            except ValidationError as e:
                return Response(data={'detail': e.messages}, status=400)

        return Response(data={'detail': 'Bad request'}, status=400)