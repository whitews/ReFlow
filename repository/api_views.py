from rest_framework import generics
from rest_framework import status
from rest_framework.authentication import \
    SessionAuthentication, \
    TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response

import django_filters

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.views.generic.detail import SingleObjectMixin

from repository.models import *
from repository.serializers import *

# Design Note: For any detail view the PermissionRequiredMixin will
# restrict access to users of that project
# For any List view, the view itself will have to restrict the list
# of objects by user


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def repository_api_root(request):
    """
    The entry endpoint of our API.
    """

    return Response({
        'compensations': reverse('compensation-list', request=request),
        'project-panels': reverse('project-panel-list', request=request),
        'site-panels': reverse('site-panel-list', request=request),
        'specimens': reverse('specimen-list', request=request),
        'projects': reverse('project-list', request=request),
        'create_samples': reverse('create-sample-list', request=request),
        'samples': reverse('sample-list', request=request),
        'sites': reverse('site-list', request=request),
        'subject_groups': reverse('subject-group-list', request=request),
        'subjects': reverse('subject-list', request=request),
        'visit_types': reverse('visit-type-list', request=request),
        'stimulations': reverse('stimulation-list', request=request),
        'processes': reverse('process-list', request=request),
        'workers': reverse('worker-list', request=request),
        'process_requests': reverse('process-request-list', request=request),
        'viable_process_requests': reverse(
            'viable-process-request-list', request=request),
    })


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def retrieve_sample(request, pk):
    sample = get_object_or_404(Sample, pk=pk)

    if not sample.has_view_permission(request.user):
        raise PermissionDenied

    response = HttpResponse(
        sample.sample_file,
        content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s' \
        % sample.original_filename
    return response


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def retrieve_sample_as_pk(request, pk):
    sample = get_object_or_404(Sample, pk=pk)

    if not sample.has_view_permission(request.user):
        raise PermissionDenied

    response = HttpResponse(
        sample.sample_file,
        content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s' \
        % str(sample.id) + '.fcs'
    return response


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def retrieve_subsample_as_csv(request, pk):
    sample = get_object_or_404(Sample, pk=pk)

    if not sample.has_view_permission(request.user):
        raise PermissionDenied

    response = HttpResponse(
        sample.get_subsample_as_csv(),
        content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' \
        % str(sample.id) + '.csv'
    return response


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def retrieve_subsample_as_numpy(request, pk):
    sample = get_object_or_404(Sample, pk=pk)

    if not sample.has_view_permission(request.user):
        raise PermissionDenied

    response = HttpResponse(
        sample.subsample.file,
        content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s' \
        % str(sample.id) + '.npy'
    return response


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def retrieve_compensation_as_csv(request, pk):
    compensation = get_object_or_404(Compensation, pk=pk)

    if not compensation.has_view_permission(request.user):
        raise PermissionDenied

    response = HttpResponse(
        compensation.get_compensation_as_csv(),
        content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' \
        % "comp_" + str(compensation.id) + '.csv'
    return response


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def retrieve_compensation_as_numpy(request, pk):
    compensation = get_object_or_404(Compensation, pk=pk)

    if not compensation.has_view_permission(request.user):
        raise PermissionDenied

    response = HttpResponse(
        compensation.compensation_file.file,
        content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s' \
        % "comp_" + str(compensation.id) + '.npy'
    return response


class LoginRequiredMixin(object):
    """
    View mixin to verify a user is logged in.
    """

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)


class PermissionRequiredMixin(SingleObjectMixin):
    """
    View mixin to verify a user has permission to a resource.
    """

    def get_object(self, *args, **kwargs):
        obj = super(PermissionRequiredMixin, self).get_object(*args, **kwargs)
        if hasattr(self, 'request'):
            request = self.request
        else:
            raise PermissionDenied

        if isinstance(obj, ProtectedModel):
            if isinstance(obj, Project):
                user_sites = Site.objects.get_sites_user_can_view(
                    request.user, obj)

                if not obj.has_view_permission(request.user) and not (
                        user_sites.count() > 0):
                    raise PermissionDenied
            elif not obj.has_view_permission(request.user):
                raise PermissionDenied

        return obj


class ProjectList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of projects.
    """

    model = Project
    serializer_class = ProjectSerializer
    filter_fields = ('project_name',)

    def get_queryset(self):
        """
        Override .get_queryset() to filter on user's projects.
        """
        queryset = Project.objects.get_projects_user_can_view(self.request.user)
        return queryset


class ProjectDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveAPIView):
    """
    API endpoint representing a single project.
    """

    model = Project
    serializer_class = ProjectSerializer


class VisitTypeList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of panels.
    """

    model = VisitType
    serializer_class = VisitTypeSerializer
    filter_fields = ('visit_type_name', 'project')

    def get_queryset(self):
        """
        Override .get_queryset() to restrict panels to projects
        to which the user belongs.
        """

        user_projects = Project.objects.get_projects_user_can_view(
            self.request.user)

        # filter on user's projects
        queryset = VisitType.objects.filter(project__in=user_projects)

        return queryset


class VisitTypeDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveAPIView):
    """
    API endpoint representing a single project.
    """

    model = VisitType
    serializer_class = VisitTypeSerializer


class SubjectGroupList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of subject groups.
    """

    model = SubjectGroup
    serializer_class = SubjectGroupSerializer
    filter_fields = ('group_name', 'project')

    def get_queryset(self):
        """
        Override .get_queryset() to restrict subject groups to projects
        to which the user belongs.
        """

        user_projects = Project.objects.get_projects_user_can_view(
            self.request.user)

        # filter on user's projects
        queryset = SubjectGroup.objects.filter(project__in=user_projects)

        return queryset


class SubjectList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of panels.
    """

    model = Subject
    serializer_class = SubjectSerializer
    filter_fields = ('subject_code', 'project')

    def get_queryset(self):
        """
        Override .get_queryset() to restrict panels to projects
        to which the user belongs.
        """

        user_projects = Project.objects.get_projects_user_can_view(
            self.request.user)

        # filter on user's projects
        queryset = Subject.objects.filter(project__in=user_projects)

        return queryset


class SubjectDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveAPIView):
    """
    API endpoint representing a single subject.
    """

    model = Subject
    serializer_class = SubjectSerializer


class ProjectPanelList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of project panels.
    """

    model = ProjectPanel
    serializer_class = ProjectPanelSerializer
    filter_fields = (
        'project',
        'panel_name',
    )

    def get_queryset(self):
        """
        Restrict project panels to projects for which
        the user has view permission.
        """
        user_projects = Project.objects.get_projects_user_can_view(
            self.request.user)

        # filter on user's projects
        queryset = ProjectPanel.objects.filter(project__in=user_projects)

        return queryset


class ProjectPanelDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveAPIView):
    """
    API endpoint representing a single project panel.
    """

    model = ProjectPanel
    serializer_class = ProjectPanelSerializer


class ProjectPanelParameterList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of parameters.
    """

    model = ProjectPanelParameter
    serializer_class = ProjectPanelParameterSerializer
    filter_fields = ('parameter_type', 'parameter_value_type')


class ProjectPanelParameterDetail(LoginRequiredMixin, generics.RetrieveAPIView):
    """
    API endpoint representing a single project.
    """

    model = ProjectPanelParameter
    serializer_class = ProjectPanelParameterSerializer
    filter_fields = ('panel_name', 'staining')


class SiteList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of sites.
    """

    model = Site
    serializer_class = SiteSerializer
    filter_fields = ('site_name', 'project')

    def get_queryset(self):
        """
        Override .get_queryset() to restrict sites for which
        the user has view permission.
        """
        queryset = Site.objects.get_sites_user_can_view(self.request.user)

        return queryset


class SiteDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveAPIView):
    """
    API endpoint representing a single site.
    """

    model = Site
    serializer_class = SiteSerializer


class SitePanelList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of site panels.
    """

    model = SitePanel
    serializer_class = SitePanelSerializer
    filter_fields = (
        'site',
        'site__project',
        'project_panel')

    def get_queryset(self):
        """
        Override .get_queryset() to restrict panels to sites
        to which the user belongs.
        """

        user_sites = Site.objects.get_sites_user_can_view(self.request.user)

        # filter on user's projects
        queryset = SitePanel.objects.filter(site__in=user_sites)

        # TODO: implement filtering by channel info: fluoro, ab, scatter, etc

        return queryset


class SitePanelDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveAPIView):
    """
    API endpoint representing a single site panel.
    """

    model = SitePanel
    serializer_class = SitePanelSerializer


class SpecimenList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of specimen types.
    """

    model = Specimen
    serializer_class = SpecimenSerializer
    filter_fields = ('specimen_name',)


class StimulationList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of stimulations.
    """

    model = Stimulation
    serializer_class = StimulationSerializer
    filter_fields = ('project', 'stimulation_name',)

    def get_queryset(self):
        """
        Results are restricted to projects to which the user belongs.
        """

        user_projects = Project.objects.get_projects_user_can_view(
            self.request.user)
        queryset = Stimulation.objects.filter(project__in=user_projects)

        return queryset


class StimulationDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveAPIView):
    """
    API endpoint representing a single stimulation.
    """

    model = Stimulation
    serializer_class = StimulationSerializer


class CreateSampleList(LoginRequiredMixin, generics.CreateAPIView):
    """
    API endpoint for creating a new Sample.
    """

    model = Sample
    serializer_class = SamplePOSTSerializer

    def post(self, request, *args, **kwargs):
        """
        Override post to ensure user has permission to add data to the site.
        Also removing the 'sample_file' field since it has the server path.
        """
        site_panel = SitePanel.objects.get(id=request.DATA['site_panel'])
        site = Site.objects.get(id=site_panel.site_id)
        if not site.has_add_permission(request.user):
            raise PermissionDenied

        response = super(CreateSampleList, self).post(request, *args, **kwargs)
        if hasattr(response, 'data'):
            if 'sample_file' in response.data:
                response.data.pop('sample_file')
        return response


class SampleFilter(django_filters.FilterSet):
    site_panel = django_filters.ModelMultipleChoiceFilter(
        queryset=SitePanel.objects.all())
    subject = django_filters.ModelMultipleChoiceFilter(
        queryset=Subject.objects.all())
    visit = django_filters.ModelMultipleChoiceFilter(
        queryset=VisitType.objects.all())
    specimen = django_filters.ModelMultipleChoiceFilter(
        queryset=Specimen.objects.all())
    original_filename = django_filters.CharFilter(lookup_type="icontains")

    class Meta:
        model = Sample
        fields = [
            'subject__project',
            'site_panel',
            'site_panel__site',
            'site_panel__project_panel',
            'subject',
            'subject__subject_code',
            'visit',
            'specimen',
            'stimulation',
            'original_filename'
        ]


class SampleList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of samples.
    """

    model = Sample
    serializer_class = SampleSerializer
    filter_class = SampleFilter

    def get_queryset(self):
        """
        Results are restricted to projects to which the user belongs.
        """

        user_sites = Site.objects.get_sites_user_can_view(self.request.user)
        queryset = Sample.objects.filter(site_panel__site__in=user_sites)

        return queryset


class SampleDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveAPIView):
    """
    API endpoint representing a single FCS sample.
    """

    model = Sample
    serializer_class = SampleSerializer


class SamplePanelUpdate(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.UpdateAPIView):
    """
    API endpoint for changing a panel for an FCS sample.
    """

    model = Sample
    serializer_class = SampleSerializer

    def patch(self, request, *args, **kwargs):
        if 'panel' in request.DATA:
            try:
                site_panel = SitePanel.objects.get(id=request.DATA['panel'])
                sample = Sample.objects.get(id=kwargs['pk'])
            except Exception as e:
                return Response(data={'detail': e.message}, status=400)

            if not sample.site_panel.site.has_add_permission(request.user):
                raise PermissionDenied

            try:
                # TODO: verify site panel change triggers new validation
                sample.site_panel = site_panel

                # Use SampleSerializer instead of the POST one to hide the
                # sample_file field (shows file path on server)
                serializer = SampleSerializer(sample)

                return Response(serializer.data, status=201)
            except ValidationError as e:
                return Response(data={'__all__': e.messages}, status=400)

        return Response(data={'__all__': 'Bad request'}, status=400)


class CompensationList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of compensations.
    """

    model = Compensation
    serializer_class = CompensationSerializer
    filter_fields = (
        'name',
        'site_panel',
        'site_panel__site',
        'site_panel__site__project')

    def get_queryset(self):
        """
        Override .get_queryset() to restrict panels to projects
        to which the user belongs.
        """

        user_sites = Site.objects.get_sites_user_can_view(self.request.user)

        # filter on user's projects
        queryset = Compensation.objects.filter(site_panel__site__in=user_sites)
        return queryset


class CompensationDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveAPIView):
    """
    API endpoint representing a single FCS sample.
    """

    model = Compensation
    serializer_class = CompensationSerializer


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
    pr = get_object_or_404(ProcessRequest, pk=pk)
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
def verify_process_request_assignment(request, pk):
    """
    Tests whether the requesting user (worker) is assigned to the
    specified ProcessRequest
    """
    pr = get_object_or_404(ProcessRequest, pk=pk)
    data = {'assignment': False}
    if pr.worker is not None and hasattr(request.user, 'worker'):
        if pr.worker == Worker.objects.get(user=request.user):
            data['assignment'] = True

    return Response(status=status.HTTP_200_OK, data=data)


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
    API endpoint representing a list of process requests for which a
    Worker can request assignment.
    """

    model = ProcessRequest
    serializer_class = ProcessRequestSerializer
    filter_fields = ('process', 'worker', 'request_user')

    def get_queryset(self):
        """
        Filter process requests to those with a 'Pending' status
        Regular users receive zero results.
        """

        if not hasattr(self.request.user, 'worker'):
            return ProcessRequest.objects.none()

        # PRs need to be in Pending status
        queryset = ProcessRequest.objects.filter(
            status='Pending')
        return queryset


class ProcessRequestDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveAPIView):
    """
    API endpoint representing a single process request.
    """

    model = ProcessRequest
    serializer_class = ProcessRequestDetailSerializer


class ProcessRequestAssignmentUpdate(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.UpdateAPIView):
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

            # check if ProcessRequest is already assigned
            if process_request.worker is not None:
                return Response(
                    data={'detail': 'Request is already assigned'}, status=400)

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