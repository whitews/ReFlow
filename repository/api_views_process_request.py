from rest_framework import generics
from rest_framework import status
from rest_framework.authentication import \
    SessionAuthentication, \
    TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.decorators import api_view
from rest_framework.response import Response

import django_filters

from django.db import transaction
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, \
    ValidationError
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.files import File

import numpy as np
import datetime
from tempfile import TemporaryFile
from string import join
import hashlib

from repository import models
from repository import serializers
from repository.api_utils import LoginRequiredMixin, PermissionRequiredMixin, \
    AdminRequiredMixin


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def retrieve_sample_cluster_events(request, pk):
    sample_cluster = get_object_or_404(models.SampleCluster, pk=pk)

    if not sample_cluster.has_view_permission(request.user):
        raise PermissionDenied

    response = HttpResponse(
        sample_cluster.events.file,
        content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s' \
        % "sc_" + str(sample_cluster.id) + '.csv'
    return response


class SubprocessCategoryFilter(django_filters.FilterSet):
    class Meta:
        model = models.SubprocessCategory
        fields = [
            'name'
        ]


class SubprocessCategoryList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of sub-process categories.
    """

    model = models.SubprocessCategory
    serializer_class = serializers.SubprocessCategorySerializer
    filter_class = SubprocessCategoryFilter
    queryset = models.SubprocessCategory.objects.all()


class SubprocessImplementationFilter(django_filters.FilterSet):

    category = django_filters.ModelMultipleChoiceFilter(
        queryset=models.SubprocessCategory.objects.all(),
        name='category')
    category_name = django_filters.CharFilter(
        name='category__name')

    class Meta:
        model = models.SubprocessImplementation
        fields = [
            'category',
            'category_name',
            'name'
        ]


class SubprocessImplementationList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of sub-process implementations.
    """

    model = models.SubprocessImplementation
    serializer_class = serializers.SubprocessImplementationSerializer
    filter_class = SubprocessImplementationFilter
    queryset = models.SubprocessImplementation.objects.all()


class SubprocessInputFilter(django_filters.FilterSet):

    category = django_filters.ModelMultipleChoiceFilter(
        queryset=models.SubprocessCategory.objects.all(),
        name='implementation__category')
    category_name = django_filters.CharFilter(
        name='implementation__category__name')
    implementation = django_filters.ModelMultipleChoiceFilter(
        queryset=models.SubprocessImplementation.objects.all(),
        name='implementation')
    implementation_name = django_filters.CharFilter(
        name='implementation__name')

    class Meta:
        model = models.SubprocessInput
        fields = [
            'category',
            'category_name',
            'implementation',
            'implementation_name',
            'name'
        ]


class SubprocessInputList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of sub-process inputs.
    """

    model = models.SubprocessInput
    serializer_class = serializers.SubprocessInputSerializer
    filter_class = SubprocessInputFilter
    queryset = models.SubprocessInput.objects.all()


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def verify_worker(request):
    """
    Tests whether the requesting user is a Worker
    """
    data = {'worker': False}
    if hasattr(request.user, 'worker'):
        data['worker'] = True

    return Response(status=status.HTTP_200_OK, data=data)


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated, IsAdminUser))
def revoke_process_request_assignment(request, pk):
    pr = get_object_or_404(models.ProcessRequest, pk=pk)
    if not pr.worker:
        return Response(status=status.HTTP_304_NOT_MODIFIED)

    pr.worker = None
    pr.status = "Pending"
    try:
        pr.save()
    except:
        return Response(status=status.HTTP_304_NOT_MODIFIED)

    return Response(status=status.HTTP_200_OK, data={})


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def complete_process_request_assignment(request, pk):
    pr = get_object_or_404(models.ProcessRequest, pk=pk)
    if not pr.worker or not hasattr(request.user, 'worker'):
        return Response(status=status.HTTP_304_NOT_MODIFIED)
    if pr.worker.user != request.user:
        return Response(status=status.HTTP_304_NOT_MODIFIED)

    pr.status = "Complete"
    try:
        pr.save()
    except:
        return Response(status=status.HTTP_304_NOT_MODIFIED)

    return Response(status=status.HTTP_200_OK, data={})


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def verify_process_request_assignment(request, pk):
    """
    Tests whether the requesting user (worker) is assigned to the
    specified ProcessRequest
    """
    pr = get_object_or_404(models.ProcessRequest, pk=pk)
    data = {'assignment': False}
    if pr.worker is not None and hasattr(request.user, 'worker'):
        if pr.worker == models.Worker.objects.get(user=request.user):
            data['assignment'] = True

    return Response(status=status.HTTP_200_OK, data=data)


class WorkerDetail(AdminRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint representing a single worker.
    """

    model = models.Worker
    serializer_class = serializers.WorkerSerializer
    queryset = models.Worker.objects.all()

    def put(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            models.Worker.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        response = super(WorkerDetail, self).put(request, *args, **kwargs)
        return response

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            worker = models.Worker.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if worker.processrequest_set.count() > 0:
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(WorkerDetail, self).delete(request, *args, **kwargs)
        return response


class WorkerList(AdminRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint representing a list of workers.
    """

    model = models.Worker
    serializer_class = serializers.WorkerSerializer
    filter_fields = ('worker_name',)
    queryset = models.Worker.objects.all()

    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(WorkerList, self).post(request, *args, **kwargs)
        return response


class SampleCollectionDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveAPIView):
    """
    API endpoint representing a single sample collection.
    """

    model = models.SampleCollection
    serializer_class = serializers.SampleCollectionDetailSerializer


class SampleCollectionMemberList(
        LoginRequiredMixin,
        generics.ListCreateAPIView):
    """
    API endpoint for listing and creating a SampleCollectionMember. Note
    this API POST takes a list of instances.
    """

    model = models.SampleCollectionMember
    serializer_class = serializers.SampleCollectionMemberSerializer
    filter_fields = ('sample_collection', 'sample')

    def get_queryset(self):
        """
        Restrict collection members to users with process permissions
        """
        user_projects = models.Project.objects.get_projects_user_can_process(
            self.request.user
        )
        queryset = models.SampleCollectionMember.objects.filter(
            sample_collection__project__in=user_projects)

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Override create to get serializer w/ many=True.

        This API handles a POST containing a list of sample collection members
        to reduce the HTTP chatter.
        """
        data = request.data

        if not isinstance(data, list):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # check the comp matrix text, see if one already exists and use
        # that FrozenCompensation id, if not create a new one
        for d in data:
            try:
                # find any matching matrices by SHA-1
                sha1 = hashlib.sha1(d['compensation']).hexdigest()
                comp = models.FrozenCompensation.objects.get(sha1=sha1)
            except ObjectDoesNotExist:
                comp = models.FrozenCompensation(matrix_text=d['compensation'])
                comp.save()

            d['compensation'] = comp.id

        serializer = self.get_serializer(data=data, many=True)
        if serializer.is_valid():
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SampleCollectionList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint for listing and creating a SampleCollection.
    """

    model = models.SampleCollection
    serializer_class = serializers.SampleCollectionSerializer
    filter_fields = ('id', 'project',)

    def get_queryset(self):
        """
        Restrict collections to users with process permissions
        """
        user_projects = models.Project.objects.get_projects_user_can_process(
            self.request.user
        )
        queryset = models.SampleCollection.objects.filter(
            project__in=user_projects)

        return queryset


class ProcessRequestList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint representing a list of process requests.
    """

    model = models.ProcessRequest
    serializer_class = serializers.ProcessRequestSerializer
    filter_fields = ('project', 'worker', 'request_user', 'parent_stage')

    def get_queryset(self):
        """
        Restrict process requests to users with process permissions
        """
        user_projects = models.Project.objects.get_projects_user_can_process(
            self.request.user
        )
        queryset = models.ProcessRequest.objects.filter(
            project__in=user_projects)

        return queryset

    def post(self, request, *args, **kwargs):
        # check permission for submitting process requests for this project
        project = get_object_or_404(models.Project, pk=request.data['project'])
        if not project.has_process_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        # add required fields for the user and status
        request.data['request_user'] = request.user.id
        request.data['status'] = 'Pending'
        response = super(ProcessRequestList, self).post(
            request,
            *args,
            **kwargs
        )
        return response


class ProcessRequestInputList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint for listing and creating a ProcessRequestInput.
    """

    model = models.ProcessRequestInput
    serializer_class = serializers.ProcessRequestInputSerializer
    filter_fields = ('process_request', 'subprocess_input')

    def get_queryset(self):
        """
        Restrict process request inputs to users with process permissions
        """
        user_projects = models.Project.objects.get_projects_user_can_process(
            self.request.user
        )
        queryset = models.ProcessRequestInput.objects.filter(
            process_request__project__in=user_projects)

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Override create to get serializer w/ many=True.

        This API handles a POST containing a list of process request inputs
        to reduce the HTTP chatter.
        """

        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProcessRequestStage2Create(LoginRequiredMixin, generics.CreateAPIView):
    """
    API endpoint for create 2nd stage process requests
    """

    model = models.ProcessRequest
    serializer_class = serializers.ProcessRequestDetailSerializer

    def create(self, request, *args, **kwargs):
        """
        Override create to handle creating nested relationships
        """

        # check permission for submitting process requests for this project
        parent_pr = get_object_or_404(
            models.ProcessRequest,
            pk=request.data['parent_pr_id']
        )
        if not parent_pr.project.has_process_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        # ensure that a cell subset label was provided and that at least
        # one cluster has been tagged with that label
        cell_subset_label = get_object_or_404(
            models.CellSubsetLabel,
            pk=request.data['cell_subset_label']
        )
        cluster_labels = cell_subset_label.clusterlabel_set.filter(
            cluster__process_request=parent_pr
        )
        if cluster_labels <= 0:
            return Response(
                data=['No clusters were found with specified label'],
                status=400
            )

        try:
            with transaction.atomic():
                pr = models.ProcessRequest(
                    project=parent_pr.project,
                    sample_collection=parent_pr.sample_collection,
                    description=request.data['description'],
                    parent_stage=parent_pr,
                    subsample_count=request.data['subsample_count'],
                    request_user=request.user,
                    status="Pending"
                )
                pr.save()

                # now create the process inputs,
                # starting w/ the parameters
                subprocess_input = models.SubprocessInput.objects.get(
                    implementation__category__name='filtering',
                    name='parameter'
                )
                for param_string in request.data['parameters']:
                    models.ProcessRequestInput.objects.create(
                        process_request=pr,
                        subprocess_input=subprocess_input,
                        value=param_string
                    )

                # next, the clusters from stage 1 to include in stage 2
                for cluster_label in cluster_labels:
                    pr2_clust = models.ProcessRequestStage2Cluster(
                        process_request=pr,
                        cluster_id=cluster_label.cluster.id
                    )
                    pr2_clust.save()

                # finally, the clustering inputs:
                #     seed, cluster count, burn-in, & iterations
                subprocess_input = models.SubprocessInput.objects.get(
                    implementation__category__name='clustering',
                    implementation__name='hdp',
                    name='random_seed'
                )
                models.ProcessRequestInput.objects.create(
                    process_request=pr,
                    subprocess_input=subprocess_input,
                    value=request.data['random_seed']
                )

                subprocess_input = models.SubprocessInput.objects.get(
                    implementation__category__name='clustering',
                    implementation__name='hdp',
                    name='cluster_count'
                )
                models.ProcessRequestInput.objects.create(
                    process_request=pr,
                    subprocess_input=subprocess_input,
                    value=request.data['cluster_count']
                )

                subprocess_input = models.SubprocessInput.objects.get(
                    implementation__category__name='clustering',
                    implementation__name='hdp',
                    name='burnin'
                )
                models.ProcessRequestInput.objects.create(
                    process_request=pr,
                    subprocess_input=subprocess_input,
                    value=request.data['burn_in_count']
                )

                subprocess_input = models.SubprocessInput.objects.get(
                    implementation__category__name='clustering',
                    implementation__name='hdp',
                    name='iteration_count'
                )
                models.ProcessRequestInput.objects.create(
                    process_request=pr,
                    subprocess_input=subprocess_input,
                    value=request.data['iteration_count']
                )

        except Exception, e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = serializers.ProcessRequestDetailSerializer(
            pr,
            context={'request': request}
        )
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class AssignedProcessRequestList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of process requests to which the
    requesting Worker is assigned.
    """

    model = models.ProcessRequest
    serializer_class = serializers.ProcessRequestSerializer

    def get_queryset(self):
        """
        Filter process requests which do not have 'Complete' status
        and is currently assigned to the requesting worker
        Regular users receive zero results.
        """

        if not hasattr(self.request.user, 'worker'):
            return models.ProcessRequest.objects.none()

        worker = models.Worker.objects.get(user=self.request.user)

        # PRs need to be in Pending status with no completion date
        queryset = models.ProcessRequest.objects.filter(
            worker=worker,
            completion_date=None,
            status__in=['Pending', 'Working']
        )
        return queryset


class ViableProcessRequestList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of process requests for which a
    Worker can request assignment.
    """

    model = models.ProcessRequest
    serializer_class = serializers.ProcessRequestSerializer
    filter_fields = ('worker', 'request_user')

    def get_queryset(self):
        """
        Filter process requests to those with a 'Pending' status
        Regular users receive zero results.
        """

        if not hasattr(self.request.user, 'worker'):
            return models.ProcessRequest.objects.none()

        # PRs need to be in Pending status with no completion date
        queryset = models.ProcessRequest.objects.filter(
            status='Pending', completion_date=None)
        return queryset


class ProcessRequestDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveDestroyAPIView):
    """
    API endpoint representing a single process request.
    """

    model = models.ProcessRequest
    serializer_class = serializers.ProcessRequestDetailSerializer

    def delete(self, request, *args, **kwargs):
        process_request = models.ProcessRequest.objects.get(id=kwargs['pk'])
        if not process_request.project.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(ProcessRequestDetail, self).delete(
            request, *args, **kwargs
        )


class ProcessRequestAssignmentUpdate(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.UpdateAPIView):
    """
    API endpoint for requesting assignment for a ProcessRequest.
    """
    # TODO: check if this is the correct serializer
    model = models.ProcessRequest
    serializer_class = serializers.ProcessRequestSerializer

    def patch(self, request, *args, **kwargs):
        """
        Override patch for validation:
          - ensure user is a Worker
          - ProcessRequest must not already be assigned
        """
        if hasattr(self.request.user, 'worker'):
            try:
                worker = models.Worker.objects.get(user=self.request.user)
                process_request = models.ProcessRequest.objects.get(
                    id=kwargs['pk']
                )
            except Exception as e:
                return Response(data={'detail': e.message}, status=400)

            # check if ProcessRequest is already assigned
            if process_request.worker is not None:
                return Response(
                    data={'detail': 'Request is already assigned'}, status=400)

            # if we get here, the worker is bonafide! "He's a suitor!"
            try:
                # now try to save the ProcessRequest
                process_request.worker = worker
                process_request.status = 'Working'
                process_request.assignment_date = datetime.datetime.now()
                process_request.save()

                # serialize the updated ProcessRequest
                serializer = serializers.ProcessRequestSerializer(
                    process_request
                )

                return Response(serializer.data, status=201)
            except ValidationError as e:
                return Response(data={'detail': e.messages}, status=400)

        return Response(data={'detail': 'Bad request'}, status=400)


class ProcessRequestReportError(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.UpdateAPIView):
    """
    API endpoint for reporting a ProcessRequest error.
    """
    # TODO: check if this is the correct serializer
    model = models.ProcessRequest
    serializer_class = serializers.ProcessRequestSerializer

    def patch(self, request, *args, **kwargs):
        """
        Override patch for validation:
          - ensure user is a Worker
          - ProcessRequest must be assigned to that worker
        """
        if hasattr(self.request.user, 'worker'):
            try:
                worker = models.Worker.objects.get(user=self.request.user)
                process_request = models.ProcessRequest.objects.get(
                    id=kwargs['pk']
                )
            except Exception as e:
                return Response(data={'detail': e.message}, status=400)

            # check that PR is assigned to this worker
            if process_request.worker.id != worker.id:
                return Response(status=status.HTTP_304_NOT_MODIFIED)

            # make sure the ProcessRequest status is Working
            if process_request.status != 'Working':
                return Response(status=status.HTTP_304_NOT_MODIFIED)

            try:
                process_request.status = 'Error'
                process_request.status_message = request.data['status_message']
                process_request.save()

                # serialize the updated ProcessRequest
                serializer = serializers.ProcessRequestSerializer(
                    process_request
                )

                return Response(serializer.data, status=201)
            except ValidationError as e:
                return Response(data={'detail': e.messages}, status=400)

        return Response(data={'detail': 'Bad request'}, status=400)


class ClusterList(
        LoginRequiredMixin,
        generics.ListCreateAPIView):
    """
    API endpoint for listing and creating a Cluster.
    """
    model = models.Cluster
    serializer_class = serializers.ClusterSerializer
    filter_fields = ('process_request',)

    def get_queryset(self):
        """
        Restrict clusters to users with process permissions
        """
        user_projects = models.Project.objects.get_projects_user_can_process(
            self.request.user
        )
        queryset = models.Cluster.objects.filter(
            process_request__project__in=user_projects)

        return queryset

    def post(self, request, *args, **kwargs):
        """
        Override post to ensure user is a worker.
        """
        if hasattr(self.request.user, 'worker'):
            try:
                worker = models.Worker.objects.get(user=self.request.user)
                process_request = models.ProcessRequest.objects.get(
                    id=request.data['process_request'])
            except Exception as e:
                return Response(data={'detail': e.message}, status=400)

            # ensure ProcessRequest is assigned to this worker
            if process_request.worker != worker:
                return Response(
                    data={
                        'detail': 'Request is not assigned to this worker'
                    },
                    status=status.HTTP_400_BAD_REQUEST)

            # if we get here, the worker is bonafide! "He's a suitor!"
            response = super(ClusterList, self).post(request, *args, **kwargs)
            return response
        return Response(
            data={'detail': 'Bad request'},
            status=status.HTTP_400_BAD_REQUEST
        )


class ClusterLabelFilter(django_filters.FilterSet):
    process_request = django_filters.ModelMultipleChoiceFilter(
        queryset=models.ProcessRequest.objects.all(),
        name='cluster__process_request'
    )
    cluster_index = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Cluster.objects.all(),
        name='cluster__cluster_index'
    )
    label_name = django_filters.ModelMultipleChoiceFilter(
        queryset=models.CellSubsetLabel.objects.all(),
        name='label__name'
    )

    class Meta:
        model = models.ClusterLabel
        fields = [
            'process_request',
            'cluster',
            'cluster_index',
            'label',
            'label_name'
        ]


class ClusterLabelList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint representing a list of cluster labels.
    """

    model = models.ClusterLabel
    serializer_class = serializers.ClusterLabelSerializer
    filter_class = ClusterLabelFilter

    def get_queryset(self):
        """
        Results are restricted to projects to which the user belongs.
        """

        user_projects = models.Project.objects.get_projects_user_can_view(
            self.request.user)
        queryset = models.ClusterLabel.objects.filter(
            label__project__in=user_projects
        )

        return queryset

    def post(self, request, *args, **kwargs):
        label = get_object_or_404(
            models.CellSubsetLabel, id=request.data['label']
        )
        cluster = get_object_or_404(
            models.Cluster, id=request.data['cluster']
        )

        # check for permission to add project data
        if not label.project.has_add_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        # check that label and cluster belong to the same project
        if cluster.process_request.project != label.project:
            return Response(
                data={
                    'detail': 'Cluster & label must belong to the same project'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        response = super(ClusterLabelList, self).post(request, *args, **kwargs)
        return response


class ClusterLabelDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveDestroyAPIView):
    """
    API endpoint representing a single cluster label.
    """

    model = models.ClusterLabel
    serializer_class = serializers.ClusterLabelSerializer

    def delete(self, request, *args, **kwargs):
        cluster_label = models.ClusterLabel.objects.get(id=kwargs['pk'])
        if not cluster_label.label.project.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(ClusterLabelDetail, self).delete(request, *args, **kwargs)


class SampleClusterFilter(django_filters.FilterSet):
    process_request = django_filters.ModelMultipleChoiceFilter(
        queryset=models.ProcessRequest.objects.all(),
        name='cluster__process_request'
    )
    cluster_index = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Cluster.objects.all(),
        name='cluster__cluster_index'
    )

    class Meta:
        model = models.SampleCluster
        fields = [
            'process_request',
            'cluster',
            'cluster_index',
            'sample'
        ]


class SampleClusterList(
        LoginRequiredMixin,
        generics.ListCreateAPIView):
    """
    API endpoint for listing and creating a SampleCluster.
    """
    model = models.SampleCluster
    serializer_class = serializers.SampleClusterSerializer
    filter_class = SampleClusterFilter

    def get_queryset(self):
        """
        Restrict sample clusters to users with process permissions
        """
        user_projects = models.Project.objects.get_projects_user_can_process(
            self.request.user
        )
        queryset = models.SampleCluster.objects.filter(
            cluster__process_request__project__in=user_projects)

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Override create to save all relations in an atomic transaction.
        Also, verify user is a worker and is assigned to this ProcessRequest
        """
        if hasattr(self.request.user, 'worker'):
            try:
                worker = models.Worker.objects.get(user=self.request.user)
                cluster = models.Cluster.objects.get(
                    id=request.data['cluster_id']
                )
            except Exception as e:
                return Response(data={'detail': e.message}, status=400)

            # ensure ProcessRequest is assigned to this worker
            if cluster.process_request.worker != worker:
                return Response(
                    data={
                        'detail': 'Request is not assigned to this worker'
                    },
                    status=400)
        else:
            # only workers can post SampleClusters
            return Response(data={'detail': 'Bad request'}, status=400)

        # if we get here, the worker is bonafide! "He's a suitor!"
        # we can create the SampleCluster instance now,
        # but we'll do so inside an atomic transaction
        try:
            sample = models.Sample.objects.get(id=request.data['sample_id'])

            with transaction.atomic():
                sample_cluster = models.SampleCluster(
                    cluster=cluster,
                    sample=sample,
                )

                # save event indices in a numpy file
                events_file = TemporaryFile()
                np.savetxt(
                    events_file,
                    np.array(request.data['events']),
                    fmt='%s',
                    delimiter=','
                )
                sample_cluster.events.save(
                    join([str(sample.id), 'csv'], '.'),
                    File(events_file),
                    save=False
                )

                sample_cluster.clean()
                sample_cluster.save()

                # now create SampleClusterParameter instances
                for param in request.data['parameters']:
                    models.SampleClusterParameter.objects.create(
                        sample_cluster=sample_cluster,
                        channel=param,
                        location=request.data['parameters'][param]
                    )

                # Finally, save all the SampleClusterComponent instances
                # along with their parameters
                for comp in request.data['components']:
                    scc = models.SampleClusterComponent.objects.create(
                        sample_cluster=sample_cluster,
                        covariance_matrix=comp['covariance'],
                        weight=comp['weight']
                    )
                    for comp_param in comp['parameters']:
                        models.SampleClusterComponentParameter.objects.create(
                            sample_cluster_component=scc,
                            channel=comp_param,
                            location=comp['parameters'][comp_param]
                        )

        except Exception as e:  # catch any exception to rollback changes
            return Response(data={'detail': e.message}, status=400)

        serializer = serializers.SampleClusterSerializer(
            sample_cluster,
            context={'request': request}
        )
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class SampleClusterComponentFilter(django_filters.FilterSet):
    process_request = django_filters.ModelMultipleChoiceFilter(
        queryset=models.ProcessRequest.objects.all(),
        name='sample_cluster__cluster__process_request'
    )
    sample = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Sample.objects.all(),
        name='sample_cluster__sample'
    )
    cluster = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Cluster.objects.all(),
        name='sample_cluster__cluster'
    )

    class Meta:
        model = models.SampleClusterComponent
        fields = [
            'process_request',
            'sample',
            'cluster'
        ]


class SampleClusterComponentList(
        LoginRequiredMixin,
        generics.ListAPIView):
    """
    API endpoint for listing and creating a SampleCluster.
    """
    model = models.SampleClusterComponent
    serializer_class = serializers.SampleClusterComponentSerializer
    filter_class = SampleClusterComponentFilter

    def get_queryset(self):
        """
        Restrict sample clusters to users with process permissions
        """
        user_projects = models.Project.objects.get_projects_user_can_process(
            self.request.user
        )
        queryset = models.SampleClusterComponent.objects.filter(
            sample_cluster__cluster__process_request__project__in=user_projects
        )

        return queryset
