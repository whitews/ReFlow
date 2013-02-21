from rest_framework import generics
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

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
        'parameters': reverse('parameter-list', request=request),
        'projects': reverse('project-list', request=request),
        'samples': reverse('sample-list', request=request),
    })


class LoginRequiredMixin(object):
    """
    View mixin to verify a user is logged in.
    """

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(
                request, *args, **kwargs)


class PermissionRequiredMixin(object):
    """
    View mixin to verify a user has permission to a resource.
    """

    def get_object(self, *args, **kwargs):
        obj = super(PermissionRequiredMixin, self).get_object(*args, **kwargs)

        if isinstance(obj, Project):
            project = obj
        elif isinstance(obj, Site):
            project = get_object_or_404(Project, site=obj)
        elif isinstance(obj, Panel):
            project = get_object_or_404(Project, site__panel=obj)
        elif isinstance(obj, Subject):
            project = get_object_or_404(Project, subject=obj)
        elif isinstance(obj, Sample):
            project = get_object_or_404(Project, subject__sample=obj)
        elif isinstance(obj, PanelParameterMap):
            project = get_object_or_404(Project, site__panel__panelparametermap=obj)
        else:
            raise PermissionDenied

        if not ProjectUserMap.objects.is_project_user(project, self.request.user):
            raise PermissionDenied

        return obj


class ProjectList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of projects.
    """

    model = Project
    serializer_class = ProjectSerializer

    def get_queryset(self):
        """
        Override .get_queryset() to filter on user's projects.
        """
        queryset = ProjectUserMap.objects.get_user_projects(self.request.user)
        return queryset


class ProjectDetail(LoginRequiredMixin, PermissionRequiredMixin, generics.RetrieveAPIView):
    """
    API endpoint representing a single project.
    """

    model = Project
    serializer_class = ProjectSerializer


class ParameterList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of parameters.
    """

    model = Parameter
    serializer_class = ParameterSerializer


class SampleList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint representing a list of samples.
    """

    model = Sample
    serializer_class = SampleSerializer
    filter_fields = ('subject', 'site', 'subject__project', 'original_filename')

    def get_queryset(self):
        """
        Override .get_queryset() to filter on the SampleParameterMap property 'name'.
        If no name is provided, all samples are returned.
        All results are restricted to projects to which the user belongs.
        """

        user_projects = ProjectUserMap.objects.get_user_projects(self.request.user)

        # filter on user's projects
        queryset = Sample.objects.filter(subject__project__in=user_projects)

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
                sampleparametermap__parameter__parameter_short_name=parameter,
                sampleparametermap__value_type__value_type_short_name=value_type,
            ).distinct()

        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SamplePOSTSerializer

        return super(SampleList, self).get_serializer_class()

    def post(self, request, *args, **kwargs):
        response = super(SampleList, self).post(request, *args, **kwargs)

        if 'panel' in request.DATA and response.status_code == 201:
            try:
                panel = Panel.objects.get(id=request.DATA['panel'])
                sample = Sample.objects.get(id=response.data['id'])

                # now try to create the sample's parameters
                apply_panel_to_sample(panel, sample)

                # need to re-serialize our sample to get the sampleparameters field updated
                # we can also use this to use the SampleSerializer instead of the POST one to not give
                # back the sample_file field containing the file path on the server
                serializer = SampleSerializer(sample)
                response.data = serializer.data
            except Exception, e:
                print e
                return response

        return response


class SampleDetail(LoginRequiredMixin, PermissionRequiredMixin, generics.RetrieveAPIView):
    """
    API endpoint representing a single FCS sample.
    """

    model = Sample
    serializer_class = SampleSerializer
