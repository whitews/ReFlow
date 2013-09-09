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
from django.db.models import Count

from repository.models import *
from repository.serializers import *
from repository.utils import apply_panel_to_sample

# Design Note: For any detail view the PermissionRequiredMixin will restrict access to users of that project
# For any List view, the view itself will have to restrict the list of objects by user


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def repository_api_root(request, format=None):
    """
    The entry endpoint of our API.
    """

    return Response({
        'compensations': reverse('compensation-list', request=request),
        'site-panels': reverse('site-panel-list', request=request),
        'specimens': reverse('specimen-list', request=request),
        'parameters': reverse('parameter-list', request=request),
        'projects': reverse('project-list', request=request),
        'sample_groups': reverse('sample-group-list', request=request),
        'create_samples': reverse('create-sample-list', request=request),
        'samples': reverse('sample-list', request=request),
        'sample-sets': reverse('sample-set-list', request=request),
        'uncategorized_samples': reverse('uncat-sample-list', request=request),
        'sites': reverse('site-list', request=request),
        'subject_groups': reverse('subject-group-list', request=request),
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
            if isinstance(obj, Project):
                user_sites = Site.objects.get_sites_user_can_view(self.request.user, obj)

                if not (obj.has_view_permission(self.request.user) or user_sites.count() > 0):
                    raise PermissionDenied
            elif not obj.has_view_permission(self.request.user):
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

        user_projects = Project.objects.get_projects_user_can_view(self.request.user)

        # filter on user's projects
        queryset = ProjectVisitType.objects.filter(project__in=user_projects)

        return queryset


class VisitTypeDetail(LoginRequiredMixin, PermissionRequiredMixin, generics.RetrieveAPIView):
    """
    API endpoint representing a single project.
    """

    model = ProjectVisitType
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
        Override .get_queryset() to restrict subject groups to projects to which the user belongs.
        """

        user_projects = Project.objects.get_projects_user_can_view(self.request.user)

        # filter on user's projects
        queryset = SubjectGroup.objects.filter(project__in=user_projects)

        return queryset


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

        user_projects = Project.objects.get_projects_user_can_view(self.request.user)

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
        Override .get_queryset() to restrict sites for which the user has view permission.
        """
        queryset = Site.objects.get_sites_user_can_view(self.request.user)

        return queryset


class SiteDetail(LoginRequiredMixin, PermissionRequiredMixin, generics.RetrieveAPIView):
    """
    API endpoint representing a single project.
    """

    model = Site
    serializer_class = SiteSerializer


class SitePanelList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of panels.
    """

    model = SitePanel
    serializer_class = SitePanelSerializer
    filter_fields = ('panel_name', 'site', 'site__project')

    def get_queryset(self):
        """
        Override .get_queryset() to restrict panels to projects to which the user belongs.
        """

        user_sites = Site.objects.get_sites_user_can_view(self.request.user)

        # filter on user's projects
        queryset = SitePanel.objects.filter(site__in=user_sites)

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


class SitePanelDetail(LoginRequiredMixin, PermissionRequiredMixin, generics.RetrieveAPIView):
    """
    API endpoint representing a single project.
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


class SampleGroupList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of subject groups.
    """

    model = SampleGroup
    serializer_class = SampleGroupSerializer
    filter_fields = ('group_name',)


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
        site = Site.objects.get(id=request.DATA['site'])
        if not site.has_add_permission(request.user):
            raise PermissionDenied

        response = super(CreateSampleList, self).post(request, *args, **kwargs)
        if hasattr(response, 'data'):
            if 'sample_file' in response.data:
                response.data.pop('sample_file')
        return response


class SampleFilter(django_filters.FilterSet):
    subject__project = django_filters.ModelMultipleChoiceFilter(queryset=Project.objects.all())
    site = django_filters.ModelMultipleChoiceFilter(queryset=Site.objects.all())
    subject = django_filters.ModelMultipleChoiceFilter(queryset=Subject.objects.all())
    visit = django_filters.ModelMultipleChoiceFilter(queryset=ProjectVisitType.objects.all())
    sample_group = django_filters.ModelMultipleChoiceFilter(queryset=SampleGroup.objects.all())
    specimen = django_filters.ModelMultipleChoiceFilter(queryset=Specimen.objects.all())
    original_filename = django_filters.CharFilter(lookup_type="icontains")
    parameter = django_filters.MultipleChoiceFilter()

    class Meta:
        model = Sample
        fields = [
            'subject__project',
            'site',
            'subject',
            'visit',
            'sample_group',
            'specimen',
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
        Override .get_queryset() to filter on the SampleParameterMap property 'name'.
        If no name is provided, all samples are returned.
        All results are restricted to projects to which the user belongs.
        """

        user_sites = Site.objects.get_sites_user_can_view(self.request.user)

        # Custom filter for specifying the exact count of parameters in a Sample
        param_count_value = self.request.QUERY_PARAMS.get('parameter_count', None)
        if param_count_value is not None and param_count_value.isdigit():
            queryset = Sample.objects\
                            .filter(site__in=user_sites)\
                            .annotate(parameter_count=Count('sampleparametermap'))\
                            .filter(parameter_count=param_count_value)
        else:
            # filter on user's projects
            queryset = Sample.objects.filter(site__in=user_sites)

        # 'parameter' may be repeated, so get as list
        parameters = self.request.QUERY_PARAMS.getlist('parameter')

        # The name property is just a concatenation of 2 related fields:
        #  - parameter__parameter_short_name
        #  - value_type__value_type_short_name (single character for H, A, W, T)
        # they are joined by a hyphen

        for value in parameters:
            parameter = value[0:-2]
            value_type = value[-1]

            queryset = queryset.filter(
                sampleparametermap__parameter__parameter_short_name=parameter,
                sampleparametermap__value_type__value_type_short_name=value_type,
            ).distinct()

        return queryset


class SampleDetail(LoginRequiredMixin, PermissionRequiredMixin, generics.RetrieveAPIView):
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
                site_panel = SitePanel.objects.get(id=request.DATA['panel'])
                sample = Sample.objects.get(id=kwargs['pk'])
            except Exception as e:
                return Response(data={'detail': e.message}, status=400)

            if not sample.site.has_add_permission(request.user):
                raise PermissionDenied

            try:
                # now try to apply panel parameters to the sample's parameters
                apply_panel_to_sample(site_panel, sample)

                # need to re-serialize our sample to get the sampleparameters field updated
                # we can also use this to use the SampleSerializer instead of the POST one
                # to not give back the sample_file field containing the file path on the server
                serializer = SampleSerializer(sample)

                return Response(serializer.data, status=201)
            except ValidationError as e:
                return Response(data={'__all__': e.messages}, status=400)

        return Response(data={'__all__': 'Bad request'}, status=400)


class UncategorizedSampleList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of samples.
    """

    model = Sample
    serializer_class = SampleSerializer
    filter_fields = (
        'subject',
        'site',
        'visit',
        'sample_group',
        'subject__project',
        'original_filename'
    )

    def get_queryset(self):
        """
        Override .get_queryset() to filter on the SampleParameterMap property 'name'.
        If no name is provided, all samples are returned.
        All results are restricted to projects to which the user belongs.
        """

        user_sites = Site.objects.get_sites_user_can_view(self.request.user)

        # first, filter by user's sites
        uncat_spm = SampleParameterMap.objects.filter(parameter=None, sample__site__in=user_sites)

        # Get the distinct sample ID as a list
        uncat_sample_ids = uncat_spm.values_list('sample__id').distinct()

        param_count_value = self.request.QUERY_PARAMS.get('parameter_count', None)
        if param_count_value is not None and param_count_value.isdigit():
            queryset = Sample.objects\
                            .filter(id__in=uncat_sample_ids)\
                            .annotate(parameter_count=Count('sampleparametermap'))\
                            .filter(parameter_count=param_count_value)
        else:
            # filter the queryset by the uncategorized sample ID list
            queryset = Sample.objects.filter(id__in=uncat_sample_ids)

        # Value may have multiple names separated by commas
        fcs_text_value = self.request.QUERY_PARAMS.get('fcs_text', None)

        if fcs_text_value is None:
            return queryset

        # The name property is just a concatenation of 2 related fields:
        #  - parameter__parameter_short_name
        #  - value_type__value_type_short_name (single character for H, A, W, T)
        # they are joined by a hyphen
        fcs_pnn_names = fcs_text_value.split(',')

        for name in fcs_pnn_names:
            queryset = queryset.filter(
                sampleparametermap__fcs_text=name,
            ).distinct()

        return queryset


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

        user_sites = Site.objects.get_sites_user_can_view(self.request.user)

        # filter on user's projects
        queryset = Compensation.objects.filter(site__in=user_sites)
        return queryset


class CompensationDetail(LoginRequiredMixin, PermissionRequiredMixin, generics.RetrieveAPIView):
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

    def post(self, request, *args, **kwargs):
        sample = Sample.objects.get(id=request.DATA['sample'])
        if not sample.site.has_add_permission(request.user):
            raise PermissionDenied

        return super(SampleCompensationCreate, self).post(request, *args, **kwargs)


class SampleSetList(LoginRequiredMixin, PermissionRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list sample sets.
    """

    model = SampleSet
    serializer_class = SampleSetListSerializer
    filter_fields = ('name', 'project')

    def get_queryset(self):
        """
        Override .get_queryset() to restrict sample sets to projects to which the user belongs.
        """

        user_projects = Project.objects.get_projects_user_can_view(self.request.user)

        # filter on user's projects
        queryset = SampleSet.objects.filter(project__in=user_projects)

        return queryset


class SampleSetDetail(LoginRequiredMixin, PermissionRequiredMixin, generics.RetrieveAPIView):
    """
    API endpoint representing a sample set.
    """

    model = SampleSet
    serializer_class = SampleSetSerializer