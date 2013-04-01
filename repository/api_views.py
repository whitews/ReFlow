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

from repository.models import *
from repository.serializers import *
from repository.utils import apply_panel_to_sample

# Design Note: For any detail view the PermissionRequiredMixin will restrict access to users of that project
# For any List view, the view itself will have to restrict the list of objects by user


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def api_root(request, format=None):
    """
    The entry endpoint of our API.
    """

    return Response({
        'compensations': reverse('compensation-list', request=request),
        'panels': reverse('panel-list', request=request),
        'parameters': reverse('parameter-list', request=request),
        'projects': reverse('project-list', request=request),
        'samples': reverse('sample-list', request=request),
        'sites': reverse('site-list', request=request),
        'subjects': reverse('subject-list', request=request),
        'visit_types': reverse('visit-type-list', request=request),
    })


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def retrieve_sample(request, pk):
    sample = get_object_or_404(Sample, pk=pk)

    if not sample.has_view_permission(request.user):
        raise PermissionDenied

    response = HttpResponse(sample.sample_file, content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s' % sample.original_filename
    return response


class LoginRequiredMixin(object):
    """
    View mixin to verify a user is logged in.
    """

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    # @method_decorator(csrf_exempt)
    # def dispatch(self, request, *args, **kwargs):
    #     return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class PermissionRequiredMixin(object):
    """
    View mixin to verify a user has permission to a resource.
    """

    def get_object(self, *args, **kwargs):
        obj = super(PermissionRequiredMixin, self).get_object(*args, **kwargs)

        if isinstance(obj, ProtectedModel):
            if not obj.has_view_permission(self.request.user):
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
        queryset = Project.objects.get_user_projects(self.request.user)
        return queryset


class ProjectDetail(LoginRequiredMixin, PermissionRequiredMixin, generics.RetrieveAPIView):
    """
    API endpoint representing a single project.
    """

    model = Project
    serializer_class = ProjectSerializer


class VisitTypeList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of panels.
    """

    model = ProjectVisitType
    serializer_class = VisitTypeSerializer
    filter_fields = ('visit_type_name', 'project')

    def get_queryset(self):
        """
        Override .get_queryset() to restrict panels to projects to which the user belongs.
        """

        user_projects = Project.objects.get_user_projects(self.request.user)

        # filter on user's projects
        queryset = ProjectVisitType.objects.filter(project__in=user_projects)

        return queryset


class VisitTypeDetail(LoginRequiredMixin, PermissionRequiredMixin, generics.RetrieveAPIView):
    """
    API endpoint representing a single project.
    """

    model = ProjectVisitType
    serializer_class = VisitTypeSerializer


class SubjectList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of panels.
    """

    model = Subject
    serializer_class = SubjectSerializer
    filter_fields = ('subject_id', 'project')

    def get_queryset(self):
        """
        Override .get_queryset() to restrict panels to projects to which the user belongs.
        """

        user_projects = Project.objects.get_user_projects(self.request.user)

        # filter on user's projects
        queryset = Subject.objects.filter(project__in=user_projects)

        return queryset


class SubjectDetail(LoginRequiredMixin, PermissionRequiredMixin, generics.RetrieveAPIView):
    """
    API endpoint representing a single project.
    """

    model = Subject
    serializer_class = SubjectSerializer


class SiteList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of panels.
    """

    model = Site
    serializer_class = SiteSerializer
    filter_fields = ('site_name', 'project')

    def get_queryset(self):
        """
        Override .get_queryset() to restrict panels to projects to which the user belongs.
        """

        user_projects = Project.objects.get_user_projects(self.request.user)

        # filter on user's projects
        queryset = Site.objects.filter(project__in=user_projects)

        return queryset


class SiteDetail(LoginRequiredMixin, PermissionRequiredMixin, generics.RetrieveAPIView):
    """
    API endpoint representing a single project.
    """

    model = Site
    serializer_class = SiteSerializer


class PanelList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of panels.
    """

    model = Panel
    serializer_class = PanelSerializer
    filter_fields = ('panel_name', 'site', 'site__project')

    def get_queryset(self):
        """
        Override .get_queryset() to restrict panels to projects to which the user belongs.
        """

        user_projects = Project.objects.get_user_projects(self.request.user)

        # filter on user's projects
        queryset = Panel.objects.filter(site__project__in=user_projects)

        # Value may have multiple names separated by commas
        name_value = self.request.QUERY_PARAMS.get('name', None)

        if name_value is None:
            return queryset

        # The name property is just a concatenation of 2 related fields:
        #  - parameter__parameter_short_name
        #  - value_type__value_type_short_name (single character for H, A, W, T)
        # they are joined by a hyphen
        names = name_value.split(',')

        for name in names:
            parameter = name[0:-2]
            value_type = name[-1]

            queryset = queryset.filter(
                panelparametermap__parameter__parameter_short_name=parameter,
                panelparametermap__value_type__value_type_short_name=value_type,
            ).distinct()

        return queryset


class PanelDetail(LoginRequiredMixin, PermissionRequiredMixin, generics.RetrieveAPIView):
    """
    API endpoint representing a single project.
    """

    model = Panel
    serializer_class = PanelSerializer


class ParameterFilter(django_filters.FilterSet):
    name_contains = django_filters.CharFilter(name='parameter_short_name', lookup_type='contains')

    class Meta:
        model = Parameter
        fields = ['parameter_short_name', 'parameter_type', 'name_contains']


class ParameterList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of parameters.
    """

    model = Parameter
    serializer_class = ParameterSerializer
    filter_class = ParameterFilter


class ParameterDetail(LoginRequiredMixin, generics.RetrieveAPIView):
    """
    API endpoint representing a single project.
    """

    model = Parameter
    serializer_class = ParameterSerializer


class SampleList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint representing a list of samples.
    """

    model = Sample
    serializer_class = SampleSerializer
    filter_fields = ('subject', 'site', 'visit', 'subject__project', 'original_filename')

    def get_queryset(self):
        """
        Override .get_queryset() to filter on the SampleParameterMap property 'name'.
        If no name is provided, all samples are returned.
        All results are restricted to projects to which the user belongs.
        """

        user_projects = Project.objects.get_user_projects(self.request.user)

        # filter on user's projects
        queryset = Sample.objects.filter(subject__project__in=user_projects)

        # Value may have multiple names separated by commas
        name_value = self.request.QUERY_PARAMS.get('parameter_names', None)

        if name_value is None:
            return queryset

        # The name property is just a concatenation of 2 related fields:
        #  - parameter__parameter_short_name
        #  - value_type__value_type_short_name (single character for H, A, W, T)
        # they are joined by a hyphen
        names = name_value.split(',')

        for name in names:
            parameter = name[0:-2]
            value_type = name[-1]

            queryset = queryset.filter(
                sampleparametermap__parameter__parameter_short_name=parameter,
                sampleparametermap__value_type__value_type_short_name=value_type,
            ).distinct()

        return queryset

    def get_serializer_class(self):
        # hack to get the POST form to display the file upload field, but avoid it on the GET list
        if self.request.method == 'GET' and hasattr(self, 'response'):
            return SamplePOSTSerializer

        if self.request.method == 'POST':
            return SamplePOSTSerializer

        return super(SampleList, self).get_serializer_class()


class SampleDetail(LoginRequiredMixin, generics.RetrieveAPIView):
    """
    API endpoint representing a single FCS sample.
    """

    model = Sample
    serializer_class = SampleSerializer


class SamplePanelUpdate(LoginRequiredMixin, PermissionRequiredMixin, generics.UpdateAPIView):
    """
    API endpoint for applying a panel to an FCS sample.
    """

    model = Sample
    serializer_class = SampleSerializer

    def patch(self, request, *args, **kwargs):
        if 'panel' in request.DATA:
            try:
                panel = Panel.objects.get(id=request.DATA['panel'])
                sample = Sample.objects.get(id=kwargs['pk'])
            except Exception as e:
                return Response(data={'detail': e.message}, status=400)

            try:
                # now try to apply panel parameters to the sample's parameters
                apply_panel_to_sample(panel, sample)

                # need to re-serialize our sample to get the sampleparameters field updated
                # we can also use this to use the SampleSerializer instead of the POST one to not give
                # back the sample_file field containing the file path on the server
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
    filter_fields = ('original_filename', 'site', 'site__project')

    def get_queryset(self):
        """
        Override .get_queryset() to restrict panels to projects to which the user belongs.
        """

        user_projects = Project.objects.get_user_projects(self.request.user)

        # filter on user's projects
        queryset = Compensation.objects.filter(site__project__in=user_projects)
        return queryset


class CompensationDetail(LoginRequiredMixin, generics.RetrieveAPIView):
    """
    API endpoint representing a single FCS sample.
    """

    model = Compensation
    serializer_class = CompensationSerializer


class SampleCompensationCreate(LoginRequiredMixin, PermissionRequiredMixin, generics.CreateAPIView):
    """
    API endpoint for associating a compensation matrix with an FCS sample.
    """

    model = SampleCompensationMap
    serializer_class = SampleCompensationPOSTSerializer
