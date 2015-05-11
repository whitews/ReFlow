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
from rest_framework.views import exception_handler
from rest_framework.exceptions import NotAuthenticated

import django_filters

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, \
    MultipleObjectsReturned
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.views.generic.detail import SingleObjectMixin

from guardian.models import UserObjectPermission
from guardian.shortcuts import assign_perm, remove_perm

import numpy as np

from repository.models import *
from repository.serializers import *
from repository.controllers import *

# Design Note: For any detail view the PermissionRequiredMixin will
# restrict access to users of that project
# For any List view, the view itself will have to restrict the list
# of objects by user


def custom_exception_handler(exc):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    if isinstance(exc, NotAuthenticated):
        response = Response({'detail': 'Not authenticated'},
                        status=status.HTTP_401_UNAUTHORIZED,
                        exception=True)
    else:
        response = exception_handler(exc)

    return response

@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def repository_api_root(request):
    """
    The entry endpoint of our API.
    """

    return Response({
        'beads': reverse('bead-list', request=request),
        'create_beads': reverse('create-bead-list', request=request),
        'compensations': reverse('compensation-list', request=request),
        'panel-templates': reverse('panel-template-list', request=request),
        'panel-variants': reverse('panel-variant-list', request=request),
        'site-panels': reverse('site-panel-list', request=request),
        'cytometers': reverse('cytometer-list', request=request),
        'markers': reverse('marker-list', request=request),
        'fluorochromes': reverse('fluorochrome-list', request=request),
        'specimens': reverse('specimen-list', request=request),
        'permissions': reverse('permission-list', request=request),
        'users': reverse('user-list', request=request),
        'projects': reverse('project-list', request=request),
        'cell_subset_labels': reverse('cell-subset-label-list', request=request),
        'create_samples': reverse('create-sample-list', request=request),
        'samples': reverse('sample-list', request=request),
        'sample_metadata': reverse('sample-metadata-list', request=request),
        'sample_collections': reverse(
            'sample-collection-list', request=request),
        'sample_collection_members': reverse(
            'sample-collection-member-list', request=request),
        'sites': reverse('site-list', request=request),
        'subject_groups': reverse('subject-group-list', request=request),
        'subjects': reverse('subject-list', request=request),
        'visit_types': reverse('visit-type-list', request=request),
        'stimulations': reverse('stimulation-list', request=request),
        'workers': reverse('worker-list', request=request),
        'subprocess_categories': reverse(
            'subprocess-category-list', request=request),
        'subprocess_implementations': reverse(
            'subprocess-implementation-list', request=request),
        'subprocess_inputs': reverse('subprocess-input-list', request=request),
        'process_requests': reverse('process-request-list', request=request),
        'process_request_stage2_create': reverse('process-request-stage2-create', request=request),
        'process_request_inputs': reverse(
            'process-request-input-list', request=request),
        'assigned_process_requests': reverse(
            'assigned-process-request-list', request=request),
        'viable_process_requests': reverse(
            'viable-process-request-list', request=request),
        'clusters': reverse('cluster-list', request=request),
        'cluster-labels': reverse('cluster-label-list', request=request),
        'sample_clusters': reverse('sample-cluster-list', request=request),
        'sample_cluster_components': reverse('sample-cluster-component-list', request=request)
    })


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def get_user_details(request):
    return Response(
        {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'superuser': request.user.is_superuser,
            'staff': request.user.is_staff
        }
    )


@api_view(['PUT'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def change_user_password(request):
    try:
        user_id = int(request.DATA['user_id'])
        current_password = request.DATA['current_password']
        new_password = request.DATA['new_password']
    except KeyError:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # users can only change their own password
    if user_id != request.user.id:
        return Response(status=status.HTTP_403_FORBIDDEN)

    # new password cannot be empty and must be different from current one
    if new_password == '' or current_password == new_password:
        return Response(
            data=["Password cannot be blank or equal to current password"],
            status=status.HTTP_400_BAD_REQUEST
        )

    if not request.user.check_password(current_password):
        return Response(
            data=["Current password is incorrect"],
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        request.user.set_password(new_password)
        request.user.save()
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def is_user(request, username):
    try:
        User.objects.get(username=username)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def get_project_permissions(request, project):
    project = get_object_or_404(Project, pk=project)

    if not (request.user in project.get_project_users() or request.user.is_superuser):
        raise PermissionDenied

    perms = project.get_user_permissions(request.user)

    return Response({'permissions': perms})


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def get_site_permissions(request, site):
    site = get_object_or_404(Site, pk=site)

    if not site.has_view_permission(request.user):
        raise PermissionDenied

    perms = site.get_user_permissions(request.user)

    return Response({'permissions': perms})


@api_view(['GET'])
def get_parameter_functions(request):
    return Response(PARAMETER_TYPE_CHOICES)


@api_view(['GET'])
def get_parameter_value_types(request):
    return Response(PARAMETER_VALUE_TYPE_CHOICES)


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
def retrieve_bead_sample(request, pk):
    bead_sample = get_object_or_404(BeadSample, pk=pk)

    if not bead_sample.has_view_permission(request.user):
        raise PermissionDenied

    response = HttpResponse(
        bead_sample.bead_file,
        content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s' \
        % bead_sample.original_filename
    return response


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def retrieve_bead_sample_as_pk(request, pk):
    bead_sample = get_object_or_404(BeadSample, pk=pk)

    if not bead_sample.has_view_permission(request.user):
        raise PermissionDenied

    response = HttpResponse(
        bead_sample.bead_file,
        content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s' \
        % str(bead_sample.id) + '.fcs'
    return response


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def retrieve_bead_subsample_as_csv(request, pk):
    bead_sample = get_object_or_404(BeadSample, pk=pk)

    if not bead_sample.has_view_permission(request.user):
        raise PermissionDenied

    response = HttpResponse(
        bead_sample.get_subsample_as_csv(),
        content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' \
        % str(bead_sample.id) + '.csv'
    return response


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def retrieve_bead_subsample_as_numpy(request, pk):
    bead_sample = get_object_or_404(BeadSample, pk=pk)

    if not bead_sample.has_view_permission(request.user):
        raise PermissionDenied

    response = HttpResponse(
        bead_sample.subsample.file,
        content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s' \
        % str(bead_sample.id) + '.npy'
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
def retrieve_compensation_as_csv_object(request, pk):
    compensation = get_object_or_404(Compensation, pk=pk)

    if not compensation.has_view_permission(request.user):
        raise PermissionDenied

    matrix = compensation.get_compensation_as_csv()

    response = Response(
        {
            'matrix': matrix.getvalue()
        }
    )
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


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def retrieve_sample_cluster_events(request, pk):
    sample_cluster = get_object_or_404(SampleCluster, pk=pk)

    if not sample_cluster.has_view_permission(request.user):
        raise PermissionDenied

    response = HttpResponse(
        sample_cluster.events.file,
        content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s' \
        % "sc_" + str(sample_cluster.id) + '.csv'
    return response


class LoginRequiredMixin(object):
    """
    View mixin to verify a user is logged in.
    """

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)


class AdminRequiredMixin(object):
    """
    View mixin to verify a user is an administrator.
    """

    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminUser)


class PermissionRequiredMixin(SingleObjectMixin):
    """
    View mixin to verify a user has permission to a resource.
    """

    def get_object(self, *args, **kwargs):
        # TODO: see if we can check HTTP method (GET, PUT, etc.) to reduce
        # duplicate code for modifying resources
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


class PermissionFilter(django_filters.FilterSet):
    model = django_filters.CharFilter(name='content_type__model')
    username = django_filters.CharFilter(name='user__username')
    permission_name = django_filters.CharFilter(name='permission__codename')

    class Meta:
        model = UserObjectPermission
        fields = [
            'object_pk',
            'model'
        ]


class PermissionDetail(LoginRequiredMixin, generics.DestroyAPIView):
    """
    API endpoint for deleting user permissions for which the requesting user
    has user management permissions.
    """

    model = UserObjectPermission
    serializer_class = PermissionSerializer

    def delete(self, request, *args, **kwargs):
        # get permission instance and user
        try:
            perm = UserObjectPermission.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if perm.content_type.name == 'project':
            project = perm.content_object
        elif perm.content_type.name == 'site':
            project = perm.content_object.project
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # ensure requesting user has user management permission for this project
        if not project.has_user_management_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        remove_perm(perm.permission.codename, perm.user, perm.content_object)

        return Response(status=status.HTTP_200_OK)


class PermissionList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint representing a list of object permissions at both the project
    and site level for all users in all projects for which the requesting user
    has user management permissions.
    """

    model = UserObjectPermission
    serializer_class = PermissionSerializer
    filter_class = PermissionFilter

    def get_queryset(self):
        """
        Override .get_queryset() to filter permissions related to projects
        for which the requesting user has user management permissions.
        """

        # get list of project IDs the user has user management privileges for
        projects = Project.objects.get_projects_user_can_manage_users(
            self.request.user).values_list('id', flat=True)

        # get list of sites for those projects
        sites = Site.objects.filter(project__in=projects)\
            .values_list('id', flat=True)

        # get project related permissions
        project_perms = UserObjectPermission.objects.filter(
            content_type__model='project',
            object_pk__in=[str(p_id) for p_id in projects]
        )

        # get site related permissions
        site_perms = UserObjectPermission.objects.filter(
            content_type__model='site',
            object_pk__in=[str(s_id) for s_id in sites]
        )

        return project_perms | site_perms

    def post(self, request, *args, **kwargs):
        project_perms = [
            'view_project_data',
            'add_project_data',
            'modify_project_data',
            'submit_process_requests',
            'manage_project_users'
        ]

        site_perms = [
            'view_site_data',
            'add_site_data',
            'modify_site_data'
        ]

        # determine if model is 'site' or 'project'
        # also check that the a valid permission was provided
        if request.DATA['model'] == 'project':
            project = Project.objects.get(id=request.DATA['object_pk'])
            if request.DATA['permission_codename'] not in project_perms:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            obj = project
        elif request.DATA['model'] == 'site':
            try:
                obj = Site.objects.get(id=request.DATA['object_pk'])
                project = obj.project
            except ObjectDoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            if request.DATA['permission_codename'] not in site_perms:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # verify user is valid
        try:
            user = User.objects.get(username=request.DATA['username'])
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # ensure requesting user has user management permission for this project
        if not project.has_user_management_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        # save the permission
        assign_perm(
            request.DATA['permission_codename'],
            user,
            obj
        )

        perm = UserObjectPermission.objects.get(
            user=user,
            object_pk=obj.id,
            permission__codename=request.DATA['permission_codename']
        )

        serializer = self.get_serializer(perm)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class UserList(generics.ListCreateAPIView):
    """
    API endpoint representing a list of ReFlow users.
    """

    model = User
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.filter(worker=None)
        return queryset

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(UserList, self).get(request, *args, **kwargs)
        return response

    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.DATA)
        if serializer.is_valid():
            try:
                # check for optional properties
                user_kwargs = {}
                if 'first_name' in serializer.init_data:
                    user_kwargs['first_name'] = serializer.init_data['first_name']
                if 'last_name' in serializer.init_data:
                    user_kwargs['last_name'] = serializer.init_data['last_name']

                # different calls needed for regular vs super users
                is_superuser = False
                if 'is_superuser' in serializer.init_data:
                    if serializer.init_data['is_superuser'] == True:
                        is_superuser = True

                if is_superuser:
                    user = User.objects.create_superuser(
                        serializer.init_data['username'],
                        email=serializer.init_data['email'],
                        password=serializer.init_data['password'],
                        **user_kwargs
                    )
                else:
                    user = User.objects.create_user(
                        serializer.init_data['username'],
                        email=serializer.init_data['email'],
                        password=serializer.init_data['password'],
                        **user_kwargs
                    )
            except IntegrityError, e:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            except Exception, e:
                # TODO: remove this after more experimentation
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint representing a single ReFlow user.
    """

    model = User
    serializer_class = UserSerializer

    def put(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)

        user = User.objects.get(id=kwargs['pk'])
        # don't allow editing workers
        if hasattr(user, 'worker'):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Only allow editing certain User attributes,
        # and calling super's put oddly resets user's date_joined & last_login
        # We don't want that, so we'll have to save the user ourselves,
        # But the fun doesn't stop there! This ends up a little messy
        # b/c you can't set model instance attributes as strings like a
        # dictionary can, so we need to set them each explicitly, then save
        try:
            if 'username' in request.DATA :
                user.username = request.DATA['username']
            if 'email' in request.DATA:
                user.email = request.DATA['email']
            if 'first_name' in request.DATA:
                user.first_name = request.DATA['first_name']
            if 'last_name' in request.DATA:
                user.last_name = request.DATA['last_name']
            if 'is_active' in request.DATA:
                user.is_active = request.DATA['is_active']
            if 'is_superuser' in request.DATA:
                user.is_superuser = request.DATA['is_superuser']
            user.save()
            return Response(status=status.HTTP_200_OK)
        except Exception, e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)
        user = User.objects.get(id=kwargs['pk'])
        if user.processrequest_set.count() == 0:
            return super(UserDetail, self).delete(request, *args, **kwargs)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class ProjectList(LoginRequiredMixin, generics.ListCreateAPIView):
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

    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(ProjectList, self).post(request, *args, **kwargs)
        return response


class ProjectDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint representing a single project.
    """

    model = Project
    serializer_class = ProjectSerializer

    def put(self, request, *args, **kwargs):
        project = Project.objects.get(id=kwargs['pk'])
        if not project.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(ProjectDetail, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        project = Project.objects.get(id=kwargs['pk'])
        if not project.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(ProjectDetail, self).delete(request, *args, **kwargs)


class ProjectUserDetail(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    generics.RetrieveUpdateAPIView):
    """
    API endpoint representing the users within a single project.
    """

    model = Project
    serializer_class = ProjectUserSerializer

    def get(self, request, *args, **kwargs):
        project = Project.objects.get(id=kwargs['pk'])

        if not project.has_user_management_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(ProjectUserDetail, self).get(request, *args, **kwargs)
        return response


class ProjectSitesByPermissionList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of project sites with the specified
    permission.
    """

    model = Site
    serializer_class = SiteSerializer

    def get_queryset(self):
        project = Project.objects.get(id=self.kwargs['pk'])

        queryset = []

        if 'permission' in self.request.QUERY_PARAMS:
            if 'add_site_data' in self.request.QUERY_PARAMS['permission']:
                queryset = Site.objects.get_sites_user_can_add(
                    self.request.user,
                    project
                )
            elif 'modify_site_data' in self.request.QUERY_PARAMS['permission']:
                queryset = Site.objects.get_sites_user_can_modify(
                    self.request.user,
                    project
                )
        return queryset


class CellSubsetLabelList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint representing a list of cell subset labels.
    """

    model = CellSubsetLabel
    serializer_class = CellSubsetLabelSerializer
    filter_fields = ('project', 'name',)

    def get_queryset(self):
        """
        Results are restricted to projects to which the user belongs.
        """

        user_projects = Project.objects.get_projects_user_can_view(
            self.request.user)
        queryset = CellSubsetLabel.objects.filter(project__in=user_projects)

        return queryset

    def post(self, request, *args, **kwargs):
        project = Project.objects.get(id=request.DATA['project'])
        if not project.has_add_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(CellSubsetLabelList, self).post(request, *args, **kwargs)
        return response


class CellSubsetLabelDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint representing a single cell subset label.
    """

    model = CellSubsetLabel
    serializer_class = CellSubsetLabelSerializer

    def put(self, request, *args, **kwargs):
        subset_label = CellSubsetLabel.objects.get(id=kwargs['pk'])
        if not subset_label.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(CellSubsetLabelDetail, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        subset_label = CellSubsetLabel.objects.get(id=kwargs['pk'])
        if not subset_label.project.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(CellSubsetLabelDetail, self).delete(request, *args, **kwargs)


class VisitTypeList(LoginRequiredMixin, generics.ListCreateAPIView):
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

    def post(self, request, *args, **kwargs):
        project = Project.objects.get(id=request.DATA['project'])
        if not project.has_add_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(VisitTypeList, self).post(request, *args, **kwargs)
        return response


class VisitTypeDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint representing a single visit type.
    """

    model = VisitType
    serializer_class = VisitTypeSerializer

    def put(self, request, *args, **kwargs):
        visit_type = VisitType.objects.get(id=kwargs['pk'])
        if not visit_type.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(VisitTypeDetail, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        visit_type = VisitType.objects.get(id=kwargs['pk'])
        if not visit_type.project.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(VisitTypeDetail, self).delete(request, *args, **kwargs)


class SubjectGroupList(LoginRequiredMixin, generics.ListCreateAPIView):
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

    def post(self, request, *args, **kwargs):
        project = Project.objects.get(id=request.DATA['project'])
        if not project.has_add_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(SubjectGroupList, self).post(request, *args, **kwargs)
        return response


class SubjectGroupDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint representing a single subject group.
    """

    model = SubjectGroup
    serializer_class = SubjectGroupSerializer

    def put(self, request, *args, **kwargs):
        subject_group = SubjectGroup.objects.get(id=kwargs['pk'])
        if not subject_group.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(SubjectGroupDetail, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        subject_group = SubjectGroup.objects.get(id=kwargs['pk'])
        if not subject_group.project.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(SubjectGroupDetail, self).delete(request, *args, **kwargs)


class SubjectList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint representing a list of subjects.
    """

    model = Subject
    serializer_class = SubjectSerializer
    filter_fields = ('subject_code', 'project', 'subject_group')

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

    def post(self, request, *args, **kwargs):
        project = Project.objects.get(id=request.DATA['project'])
        if not project.has_add_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(SubjectList, self).post(request, *args, **kwargs)
        return response


class SubjectDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint representing a single subject.
    """

    model = Subject
    serializer_class = SubjectSerializer

    def put(self, request, *args, **kwargs):
        subject = Subject.objects.get(id=kwargs['pk'])
        if not subject.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(SubjectDetail, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        subject = Subject.objects.get(id=kwargs['pk'])
        if not subject.project.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(SubjectDetail, self).delete(request, *args, **kwargs)


class PanelTemplateFilter(django_filters.FilterSet):
    project = django_filters.ModelMultipleChoiceFilter(
        queryset=Project.objects.all(),
        name='project')

    class Meta:
        model = PanelTemplate
        fields = [
            'project',
            'panel_name'
        ]


class PanelTemplateList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint representing a list of panel templates.
    """

    model = PanelTemplate
    serializer_class = PanelTemplateSerializer
    filter_class = PanelTemplateFilter

    def get_queryset(self):
        """
        Restrict panel templates to projects for which
        the user has view permission.
        """
        user_projects = Project.objects.get_projects_user_can_view(
            self.request.user)

        # filter on user's projects
        queryset = PanelTemplate.objects.filter(project__in=user_projects)

        return queryset

    def create(self, request, *args, **kwargs):
        data = request.DATA

        # validate all the template components
        errors = validate_panel_template_request(data, request.user)
        if len(errors) > 0:
            return Response(data=errors, status=400)

        # we can create the PanelTemplate instance now, but we'll do so inside
        # an atomic transaction
        try:
            project = Project.objects.get(id=data['project'])

            with transaction.atomic():
                panel_template = PanelTemplate(
                    project=project,
                    panel_name=data['panel_name'],
                    panel_description=data['panel_description']
                )
                panel_template.clean()
                panel_template.save()

                for param in data['parameters']:
                    if (param['fluorochrome']):
                        param_fluoro = Fluorochrome.objects.get(
                            id=param['fluorochrome'])
                    else:
                        param_fluoro = None

                    ppp = PanelTemplateParameter.objects.create(
                        panel_template=panel_template,
                        parameter_type=param['parameter_type'],
                        parameter_value_type=param['parameter_value_type'],
                        fluorochrome=param_fluoro
                    )
                    for marker in param['markers']:
                        PanelTemplateParameterMarker.objects.create(
                            panel_template_parameter=ppp,
                            marker=Marker.objects.get(id=marker)
                        )

                # by default, every panel template gets a full stain variant
                PanelVariant.objects.create(
                    panel_template=panel_template,
                    staining_type = 'FULL'
                )

        except Exception as e:  # catch any exception to rollback changes
            return Response(data={'detail': e.message}, status=400)

        serializer = PanelTemplateSerializer(
            panel_template,
            context={'request': request}
        )
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class PanelTemplateDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving or updating a single panel template.
    """

    model = PanelTemplate
    serializer_class = PanelTemplateSerializer

    def put(self, request, *args, **kwargs):
        data = request.DATA

        # first, check if template has any site panels, editing templates
        # with existing site panels is not allowed
        panel_template = PanelTemplate.objects.get(id=kwargs['pk'])
        if panel_template.sitepanel_set.count() > 0:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # validate all the template components
        errors = validate_panel_template_request(data, request.user)
        if len(errors) > 0:
            return Response(data=errors, status=400)

        # we can create the PanelTemplate instance now, but we'll do so inside
        # an atomic transaction
        try:
            project = Project.objects.get(id=data['project'])

            with transaction.atomic():
                panel_template.project = project
                panel_template.panel_name = data['panel_name']
                panel_template.panel_description = data['panel_description']

                panel_template.clean()
                panel_template.save()

                panel_template.paneltemplateparameter_set.all().delete()

                for param in data['parameters']:
                    if (param['fluorochrome']):
                        param_fluoro = Fluorochrome.objects.get(
                            id=param['fluorochrome'])
                    else:
                        param_fluoro = None

                    ppp = PanelTemplateParameter.objects.create(
                        panel_template=panel_template,
                        parameter_type=param['parameter_type'],
                        parameter_value_type=param['parameter_value_type'],
                        fluorochrome=param_fluoro
                    )
                    for marker in param['markers']:
                        PanelTemplateParameterMarker.objects.create(
                            panel_template_parameter=ppp,
                            marker=Marker.objects.get(id=marker)
                        )
        except Exception as e:  # catch any exception to rollback changes
            return Response(data={'detail': e.message}, status=400)

        serializer = PanelTemplateSerializer(
            panel_template,
            context={'request': request}
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        panel_template = PanelTemplate.objects.get(id=kwargs['pk'])
        if not panel_template.project.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(PanelTemplateDetail, self).delete(request, *args, **kwargs)


class PanelVariantList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint representing a list of panel variants.
    """

    model = PanelVariant
    serializer_class = PanelVariantSerializer
    filter_fields = ('panel_template', 'staining_type', 'name')

    def get_queryset(self):
        """
        Override .get_queryset() to restrict panels to projects
        to which the user belongs.
        """

        user_projects = Project.objects.get_projects_user_can_view(
            self.request.user)

        # filter on user's projects
        queryset = PanelVariant.objects.filter(panel_template__project__in=user_projects)

        return queryset

    def post(self, request, *args, **kwargs):
        panel_template = PanelTemplate.objects.get(id=request.DATA['panel_template'])
        if not panel_template.project.has_add_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(PanelVariantList, self).post(request, *args, **kwargs)
        return response


class PanelVariantDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint representing a single subject.
    """

    model = PanelVariant
    serializer_class = PanelVariantSerializer

    def put(self, request, *args, **kwargs):
        panel_variant = PanelVariant.objects.get(id=kwargs['pk'])
        if not panel_variant.panel_template.project.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(PanelVariantDetail, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        panel_variant = PanelVariant.objects.get(id=kwargs['pk'])
        if not panel_variant.panel_template.project.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(PanelVariantDetail, self).delete(request, *args, **kwargs)


class SiteList(LoginRequiredMixin, generics.ListCreateAPIView):
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

    def post(self, request, *args, **kwargs):
        project = Project.objects.get(id=request.DATA['project'])
        if not project.has_add_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(SiteList, self).post(request, *args, **kwargs)
        return response


class SiteDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint representing a single site.
    """

    model = Site
    serializer_class = SiteSerializer

    def put(self, request, *args, **kwargs):
        site = Site.objects.get(id=kwargs['pk'])
        if not site.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(SiteDetail, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        site = Site.objects.get(id=kwargs['pk'])
        if not site.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(SiteDetail, self).delete(request, *args, **kwargs)


class SitePanelFilter(django_filters.FilterSet):
    panel_template = django_filters.ModelMultipleChoiceFilter(
        queryset=PanelTemplate.objects.all(),
        name='panel_template')
    site = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        name='site')
    project = django_filters.ModelMultipleChoiceFilter(
        queryset=Project.objects.all(),
        name='panel_template__project')
    fluorochrome = django_filters.ModelMultipleChoiceFilter(
        queryset=Fluorochrome.objects.all(),
        name='sitepanelparameter__fluorochrome'
    )
    fluorochrome_abbreviation = django_filters.CharFilter(
        name='sitepanelparameter__fluorochrome__fluorochrome_abbreviation'
    )

    class Meta:
        model = SitePanel
        fields = [
            'site',
            'panel_template',
            'project',
            'fluorochrome',
            'fluorochrome_abbreviation'
        ]


class SitePanelList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint representing a list of site panels.
    """

    model = SitePanel
    serializer_class = SitePanelSerializer
    filter_class = SitePanelFilter

    def get_queryset(self):
        """
        Override .get_queryset() to restrict panels to sites
        to which the user belongs.
        """

        user_sites = Site.objects.get_sites_user_can_view(self.request.user)

        # need to filter by multiple IDs but django-filter doesn't seem to like
        # that, so we'll do it ourselves here

        # filter on user's projects
        queryset = SitePanel.objects.filter(site__in=user_sites)

        id_value = self.request.QUERY_PARAMS.get('id', None)
        if id_value:
            id_list = id_value.split(',')
            queryset = queryset.filter(id__in=id_list)

        # TODO: implement filtering by channel info: fluoro, marker, scatter

        return queryset

    def create(self, request, *args, **kwargs):
        data = request.DATA

        # validate all the site panel components
        errors = validate_site_panel_request(data, request.user)
        if len(errors) > 0:
            return Response(data=errors, status=400)

        # we can create the SitePanel instance now, but we'll do so inside
        # an atomic transaction
        try:
            site = Site.objects.get(id=data['site'])
            panel_template = PanelTemplate.objects.get(id=data['panel_template'])

            with transaction.atomic():
                site_panel = SitePanel(
                    site=site,
                    panel_template=panel_template,
                    site_panel_comments=data['site_panel_comments']
                )
                site_panel.clean()
                site_panel.save()

                for param in data['parameters']:
                    if (param['fluorochrome']):
                        param_fluoro = Fluorochrome.objects.get(
                            id=param['fluorochrome'])
                    else:
                        param_fluoro = None

                    spp = SitePanelParameter.objects.create(
                        site_panel=site_panel,
                        parameter_type=param['parameter_type'],
                        parameter_value_type=param['parameter_value_type'],
                        fluorochrome=param_fluoro,
                        fcs_number=param['fcs_number'],
                        fcs_text=param['fcs_text'],
                        fcs_opt_text=param['fcs_opt_text']
                    )
                    for marker in param['markers']:
                        SitePanelParameterMarker.objects.create(
                            site_panel_parameter=spp,
                            marker=Marker.objects.get(id=marker)
                        )
        except Exception as e:  # catch any exception to rollback changes
            return Response(data={'detail': e.message}, status=400)

        serializer = SitePanelSerializer(
            site_panel,
            context={'request': request}
        )
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class SitePanelDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveDestroyAPIView):
    """
    API endpoint representing a single site panel.
    """

    model = SitePanel
    serializer_class = SitePanelSerializer

    def delete(self, request, *args, **kwargs):
        site_panel = SitePanel.objects.get(id=kwargs['pk'])
        if not site_panel.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(SitePanelDetail, self).delete(request, *args, **kwargs)


class CytometerFilter(django_filters.FilterSet):

    site = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        name='site')
    site_name = django_filters.MultipleChoiceFilter(
        choices=Site.objects.all().values_list('site_name', 'id'),
        name='site__site_name')
    project = django_filters.ModelMultipleChoiceFilter(
        queryset=Project.objects.all(),
        name='site__project')

    class Meta:
        model = Cytometer
        fields = [
            'site',
            'site_name',
            'project',
            'cytometer_name',
            'serial_number'
        ]


class CytometerList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint representing a list of cytometers.
    """

    model = Cytometer
    serializer_class = CytometerSerializer
    filter_class = CytometerFilter

    def get_queryset(self):
        """
        Override .get_queryset() to restrict panels to sites
        to which the user belongs.
        """

        user_sites = Site.objects.get_sites_user_can_view(self.request.user)

        # filter on user's projects
        queryset = Cytometer.objects.filter(site__in=user_sites)

        return queryset

    def post(self, request, *args, **kwargs):
        site = Site.objects.get(id=request.DATA['site'])
        if not site.has_add_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(CytometerList, self).post(request, *args, **kwargs)
        return response


class CytometerDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint representing a single cytometer.
    """

    model = Cytometer
    serializer_class = CytometerSerializer

    def put(self, request, *args, **kwargs):
        cytometer = Cytometer.objects.get(id=kwargs['pk'])
        if not cytometer.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(CytometerDetail, self).put(request, *args, **kwargs)
        return response

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        cytometer = Cytometer.objects.get(id=kwargs['pk'])
        if not cytometer.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(CytometerDetail, self).delete(request, *args, **kwargs)


class MarkerList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint representing a list of markers.
    """

    model = Marker
    serializer_class = MarkerSerializer
    filter_fields = ('project', 'marker_abbreviation')

    def get_queryset(self):
        """
        Results are restricted to projects to which the user belongs.
        """

        user_projects = Project.objects.get_projects_user_can_view(
            self.request.user)
        queryset = Marker.objects.filter(project__in=user_projects)

        return queryset

    def post(self, request, *args, **kwargs):
        project = Project.objects.get(id=request.DATA['project'])
        if not project.has_add_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(MarkerList, self).post(request, *args, **kwargs)
        return response


class MarkerDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint representing a single marker.
    """

    model = Marker
    serializer_class = MarkerSerializer

    def put(self, request, *args, **kwargs):
        try:
            marker = Marker.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not marker.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(MarkerDetail, self).put(request, *args, **kwargs)
        return response

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        try:
            marker = Marker.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not marker.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        if marker.sitepanelparametermarker_set.count() > 0:
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(MarkerDetail, self).delete(request, *args, **kwargs)
        return response


class FluorochromeList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint representing a list of fluorochromes.
    """

    model = Fluorochrome
    serializer_class = FluorochromeSerializer
    filter_fields = ('project', 'fluorochrome_abbreviation')

    def get_queryset(self):
        """
        Results are restricted to projects to which the user belongs.
        """

        user_projects = Project.objects.get_projects_user_can_view(
            self.request.user)
        queryset = Fluorochrome.objects.filter(project__in=user_projects)

        return queryset

    def post(self, request, *args, **kwargs):
        project = Project.objects.get(id=request.DATA['project'])
        if not project.has_add_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(FluorochromeList, self).post(request, *args, **kwargs)
        return response


class FluorochromeDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint representing a single fluorochrome.
    """

    model = Fluorochrome
    serializer_class = FluorochromeSerializer

    def put(self, request, *args, **kwargs):
        try:
            fluorochrome = Fluorochrome.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not fluorochrome.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(FluorochromeDetail, self).put(request, *args, **kwargs)
        return response

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        try:
            fluorochrome = Fluorochrome.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not fluorochrome.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        if fluorochrome.sitepanelparameter_set.count() > 0:
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(FluorochromeDetail, self).delete(request, *args, **kwargs)
        return response


class SpecimenList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint representing a list of specimen types.
    """

    model = Specimen
    serializer_class = SpecimenSerializer
    filter_fields = ('specimen_name',)

    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(SpecimenList, self).post(request, *args, **kwargs)
        return response


class SpecimenDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint representing a single fluorochrome.
    """

    model = Specimen
    serializer_class = SpecimenSerializer

    def put(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            Specimen.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        response = super(SpecimenDetail, self).put(request, *args, **kwargs)
        return response

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            specimen = Specimen.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if specimen.sample_set.count() > 0:
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(SpecimenDetail, self).delete(request, *args, **kwargs)
        return response


class StimulationList(LoginRequiredMixin, generics.ListCreateAPIView):
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

    def post(self, request, *args, **kwargs):
        project = Project.objects.get(id=request.DATA['project'])
        if not project.has_add_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(StimulationList, self).post(request, *args, **kwargs)
        return response


class StimulationDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint representing a single stimulation.
    """

    model = Stimulation
    serializer_class = StimulationSerializer

    def put(self, request, *args, **kwargs):
        stimulation = Stimulation.objects.get(id=kwargs['pk'])
        if not stimulation.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(StimulationDetail, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        stimulation = Stimulation.objects.get(id=kwargs['pk'])
        if not stimulation.project.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(StimulationDetail, self).delete(request, *args, **kwargs)


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
    panel = django_filters.ModelMultipleChoiceFilter(
        queryset=PanelTemplate.objects.all(),
        name='site_panel__panel_template')
    project = django_filters.ModelMultipleChoiceFilter(
        queryset=Project.objects.all(),
        name='site_panel__panel_template__project')
    site = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        name='site_panel__site')
    panel_variant = django_filters.ModelMultipleChoiceFilter(
        queryset=PanelVariant.objects.all())
    site_panel = django_filters.ModelMultipleChoiceFilter(
        queryset=SitePanel.objects.all())
    cytometer = django_filters.ModelMultipleChoiceFilter(
        queryset=Cytometer.objects.all(),
        name='cytometer')
    subject = django_filters.ModelMultipleChoiceFilter(
        queryset=Subject.objects.all())
    subject_group = django_filters.ModelMultipleChoiceFilter(
        queryset=SubjectGroup.objects.all(),
        name='subject__subject_group')
    subject_code = django_filters.CharFilter(
        name='subject__subject_code')
    visit = django_filters.ModelMultipleChoiceFilter(
        queryset=VisitType.objects.all(),
        name='visit')
    specimen = django_filters.ModelMultipleChoiceFilter(
        queryset=Specimen.objects.all(),
        name='specimen')
    stimulation = django_filters.ModelMultipleChoiceFilter(
        queryset=Stimulation.objects.all(),
        name='stimulation')
    original_filename = django_filters.CharFilter(lookup_type="icontains")

    class Meta:
        model = Sample
        fields = [
            'acquisition_date',
            'sha1'
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
        queryset = Sample.objects.filter(
            site_panel__site__in=user_sites)

        return queryset


class SampleDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint representing a single FCS sample.
    """

    model = Sample
    serializer_class = SampleSerializer

    def put(self, request, *args, **kwargs):
        sample = Sample.objects.get(id=request.DATA['id'])
        if not sample.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(SampleDetail, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        sample = Sample.objects.get(id=kwargs['pk'])
        if not sample.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(SampleDetail, self).delete(request, *args, **kwargs)


class SampleMetaDataList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of sample metadata.
    """

    model = SampleMetadata
    serializer_class = SampleMetadataSerializer
    filter_fields = ('id', 'sample', 'key', 'value')

    def get_queryset(self):
        """
        Override .get_queryset() to restrict sites for which
        the user has view permission.
        """
        user_sites = Site.objects.get_sites_user_can_view(self.request.user)
        queryset = SampleMetadata.objects.filter(
            sample__site_panel__site__in=user_sites)

        return queryset


class SampleCollectionMemberList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint for listing and creating a SampleCollectionMember. Note
    this API POST takes a list of instances.
    """

    model = SampleCollectionMember
    serializer_class = SampleCollectionMemberSerializer
    filter_fields = ('sample_collection', 'sample')

    def create(self, request, *args, **kwargs):
        data = request.DATA

        if not isinstance(data, list):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # check the comp matrix text, see if one already exists and use
        # that FrozenCompensation id, if not create a new one
        for d in data:
            try:
                # find any matching matrices by SHA-1
                sha1 = hashlib.sha1(d['compensation']).hexdigest()
                comp = FrozenCompensation.objects.get(sha1=sha1)
            except ObjectDoesNotExist:
                comp = FrozenCompensation(matrix_text=d['compensation'])
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

    model = SampleCollection
    serializer_class = SampleCollectionSerializer
    filter_fields = ('id', 'project',)


class SampleCollectionDetail(
        LoginRequiredMixin,
        generics.RetrieveAPIView):
    """
    API endpoint representing a single sample collection.
    """

    model = SampleCollection
    serializer_class = SampleCollectionDetailSerializer


class CreateBeadList(LoginRequiredMixin, generics.CreateAPIView):
    """
    API endpoint for creating a new Sample.
    """

    model = BeadSample
    serializer_class = BeadSamplePOSTSerializer

    def post(self, request, *args, **kwargs):
        """
        Override post to ensure user has permission to add data to the site.
        Also removing the 'sample_file' field since it has the server path.
        """
        site_panel = SitePanel.objects.get(id=request.DATA['site_panel'])
        site = Site.objects.get(id=site_panel.site_id)
        if not site.has_add_permission(request.user):
            raise PermissionDenied

        response = super(CreateBeadList, self).post(request, *args, **kwargs)
        if hasattr(response, 'data'):
            if 'bead_file' in response.data:
                response.data.pop('bead_file')
        return response


class BeadFilter(django_filters.FilterSet):
    panel_template = django_filters.ModelMultipleChoiceFilter(
        queryset=PanelTemplate.objects.all(),
        name='site_panel__panel_template')
    site = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        name='site_panel__site')
    site_panel = django_filters.ModelMultipleChoiceFilter(
        queryset=SitePanel.objects.all())
    cytometer = django_filters.ModelMultipleChoiceFilter(
        queryset=Cytometer.objects.all())
    original_filename = django_filters.CharFilter(lookup_type="icontains")

    class Meta:
        model = BeadSample
        fields = [
            'site_panel__panel_template__project',
            'site_panel',
            'site_panel__site',
            'site_panel__panel_template',
            'acquisition_date',
            'original_filename',
            'cytometer',
            'sha1'
        ]


class BeadList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of samples.
    """

    model = BeadSample
    serializer_class = BeadSampleSerializer
    filter_class = BeadFilter

    def get_queryset(self):
        """
        Results are restricted to projects to which the user belongs.
        """

        user_sites = Site.objects.get_sites_user_can_view(self.request.user)
        queryset = BeadSample.objects.filter(
            site_panel__site__in=user_sites)

        return queryset


class BeadDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint representing a single FCS sample.
    """

    model = BeadSample
    serializer_class = BeadSampleSerializer

    def put(self, request, *args, **kwargs):
        bead_sample = BeadSample.objects.get(id=request.DATA['id'])
        if not bead_sample.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(BeadDetail, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        bead_sample = BeadSample.objects.get(id=kwargs['pk'])
        if not bead_sample.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(BeadDetail, self).delete(request, *args, **kwargs)


class CompensationFilter(django_filters.FilterSet):

    site = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        name='site_panel__site')
    site_panel = django_filters.ModelMultipleChoiceFilter(
        queryset=SitePanel.objects.all(),
        name='site_panel')
    project = django_filters.ModelMultipleChoiceFilter(
        queryset=Project.objects.all(),
        name='site_panel__site__project')

    class Meta:
        model = Compensation
        fields = [
            'name',
            'acquisition_date',
            'site_panel',
            'site',
            'project'
        ]


class CompensationList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint for listing/creating compensations.
    """

    model = Compensation
    serializer_class = CompensationSerializer
    filter_class = CompensationFilter

    def get_queryset(self):
        """
        Override .get_queryset() to restrict panels to projects
        to which the user belongs.
        """
        user_sites = Site.objects.get_sites_user_can_view(self.request.user)

        # filter on user's sites
        queryset = Compensation.objects.filter(
            site_panel__site__in=user_sites)
        return queryset

    def post(self, request, *args, **kwargs):
        """
        Override post to ensure user has permission to add data to the site.
        """
        panel_template = get_object_or_404(
            PanelTemplate, id=request.DATA['panel_template'])
        site = get_object_or_404(Site, id=request.DATA['site'])
        if not site.has_add_permission(request.user):
            raise PermissionDenied

        matrix_text = request.DATA['matrix_text'].splitlines(False)
        if not len(matrix_text) > 1:
            raise ValidationError("Too few rows.")

        # first row should be headers matching the PnN value (fcs_text field)
        # may be tab or comma delimited
        # (spaces can't be delimiters b/c they are allowed in the PnN value)
        pnn_list = re.split('\t|,\s*', matrix_text[0])

        site_panel = find_matching_site_panel(pnn_list, panel_template, site)

        if site_panel:
            request.DATA['site_panel'] = site_panel.id

        response = super(CompensationList, self).post(request, *args, **kwargs)

        if not site_panel and response.status_code != 201:
            response.data['site_panel_match'] = False
        return response


class CompensationDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint representing a single FCS sample.
    """

    model = Compensation
    serializer_class = CompensationSerializer

    def put(self, request, *args, **kwargs):
        bead_sample = BeadSample.objects.get(id=request.DATA['id'])
        if not bead_sample.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(CompensationDetail, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        compensation = Compensation.objects.get(id=kwargs['pk'])
        if not compensation.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(CompensationDetail, self).delete(request, *args, **kwargs)


class SubprocessCategoryFilter(django_filters.FilterSet):
    class Meta:
        model = SubprocessCategory
        fields = [
            'name'
        ]


class SubprocessCategoryList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of sub-process categories.
    """

    model = SubprocessCategory
    serializer_class = SubprocessCategorySerializer
    filter_class = SubprocessCategoryFilter


class SubprocessImplementationFilter(django_filters.FilterSet):

    category = django_filters.ModelMultipleChoiceFilter(
        queryset=SubprocessCategory.objects.all(),
        name='category')
    category_name = django_filters.CharFilter(
        name='category__name')

    class Meta:
        model = SubprocessImplementation
        fields = [
            'category',
            'category_name',
            'name'
        ]


class SubprocessImplementationList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of sub-process implementations.
    """

    model = SubprocessImplementation
    serializer_class = SubprocessImplementationSerializer
    filter_class = SubprocessImplementationFilter


class SubprocessInputFilter(django_filters.FilterSet):

    category = django_filters.ModelMultipleChoiceFilter(
        queryset=SubprocessCategory.objects.all(),
        name='implementation__category')
    category_name = django_filters.CharFilter(
        name='implementation__category__name')
    implementation = django_filters.ModelMultipleChoiceFilter(
        queryset=SubprocessImplementation.objects.all(),
        name='implementation')
    implementation_name = django_filters.CharFilter(
        name='implementation__name')

    class Meta:
        model = SubprocessInput
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

    model = SubprocessInput
    serializer_class = SubprocessInputSerializer
    filter_class = SubprocessInputFilter


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
def complete_process_request_assignment(request, pk):
    pr = get_object_or_404(ProcessRequest, pk=pk)
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
    pr = get_object_or_404(ProcessRequest, pk=pk)
    data = {'assignment': False}
    if pr.worker is not None and hasattr(request.user, 'worker'):
        if pr.worker == Worker.objects.get(user=request.user):
            data['assignment'] = True

    return Response(status=status.HTTP_200_OK, data=data)


class WorkerDetail(AdminRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint representing a single worker.
    """

    model = Worker
    serializer_class = WorkerSerializer

    def put(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            Worker.objects.get(id=kwargs['pk'])
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
            worker = Worker.objects.get(id=kwargs['pk'])
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

    model = Worker
    serializer_class = WorkerSerializer
    filter_fields = ('worker_name',)

    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(WorkerList, self).post(request, *args, **kwargs)
        return response


class ProcessRequestList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint representing a list of process requests.
    """

    model = ProcessRequest
    serializer_class = ProcessRequestSerializer
    filter_fields = ('project', 'worker', 'request_user')

    def create(self, request, *args, **kwargs):
        # check permission for submitting process requests for this project
        project = get_object_or_404(Project, pk=request.DATA['project'])
        if not project.has_process_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        # add required fields for the user and status
        request.DATA['request_user'] = request.user.id
        request.DATA['status'] = 'Pending'
        response = super(ProcessRequestList, self).create(request, *args, **kwargs)
        return response


class ProcessRequestInputList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint for listing and creating a ProcessRequestInput.
    """

    model = ProcessRequestInput
    serializer_class = ProcessRequestInputSerializer
    filter_fields = ('process_request', 'subprocess_input')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, many=True)
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

    model = ProcessRequest
    serializer_class = ProcessRequestSerializer

    def create(self, request, *args, **kwargs):
        # check permission for submitting process requests for this project
        parent_pr = get_object_or_404(
            ProcessRequest,
            pk=request.DATA['parent_pr_id']
        )
        if not parent_pr.project.has_process_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            with transaction.atomic():
                pr = ProcessRequest(
                    project=parent_pr.project,
                    sample_collection=parent_pr.sample_collection,
                    description=request.DATA['description'],
                    parent_stage=parent_pr,
                    subsample_count=request.DATA['subsample_count'],
                    request_user=request.user,
                    status="Pending"
                )
                pr.save()

                # now create the process inputs,
                # starting w/ the parameters
                subprocess_input = SubprocessInput.objects.get(
                    implementation__category__name='filtering',
                    name='parameter'
                )
                for param_string in request.DATA['parameters']:
                    ProcessRequestInput.objects.create(
                        process_request=pr,
                        subprocess_input=subprocess_input,
                        value=param_string
                    )
                # next, the clusters from stage 1 to include in stage 2
                for cluster in request.DATA['clusters']:
                    ProcessRequestStage2Cluster.objects.create(
                        process_request=pr,
                        cluster_id=cluster
                    )

                # finally, the clustering inputs:
                #     cluster count, burn-in, & iterations
                subprocess_input = SubprocessInput.objects.get(
                    implementation__category__name='clustering',
                    implementation__name='hdp',
                    name='cluster_count'
                )
                ProcessRequestInput.objects.create(
                    process_request=pr,
                    subprocess_input=subprocess_input,
                    value=request.DATA['cluster_count']
                )

                subprocess_input = SubprocessInput.objects.get(
                    implementation__category__name='clustering',
                    implementation__name='hdp',
                    name='burnin'
                )
                ProcessRequestInput.objects.create(
                    process_request=pr,
                    subprocess_input=subprocess_input,
                    value=request.DATA['burn_in_count']
                )

                subprocess_input = SubprocessInput.objects.get(
                    implementation__category__name='clustering',
                    implementation__name='hdp',
                    name='iteration_count'
                )
                ProcessRequestInput.objects.create(
                    process_request=pr,
                    subprocess_input=subprocess_input,
                    value=request.DATA['iteration_count']
                )

        except Exception, e:
            print e

        serializer = ProcessRequestSerializer(
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

    model = ProcessRequest
    serializer_class = ProcessRequestSerializer

    def get_queryset(self):
        """
        Filter process requests which do not have 'Completed' status
        and is currently assigned to the requesting worker
        Regular users receive zero results.
        """

        if not hasattr(self.request.user, 'worker'):
            return ProcessRequest.objects.none()

        worker = Worker.objects.get(user=self.request.user)

        # PRs need to be in Pending status with no completion date
        queryset = ProcessRequest.objects.filter(
            worker=worker, completion_date=None).exclude(
                status='Completed')
        return queryset


class ViableProcessRequestList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of process requests for which a
    Worker can request assignment.
    """

    model = ProcessRequest
    serializer_class = ProcessRequestSerializer
    filter_fields = ('worker', 'request_user')

    def get_queryset(self):
        """
        Filter process requests to those with a 'Pending' status
        Regular users receive zero results.
        """

        if not hasattr(self.request.user, 'worker'):
            return ProcessRequest.objects.none()

        # PRs need to be in Pending status with no completion date
        queryset = ProcessRequest.objects.filter(
            status='Pending', completion_date=None)
        return queryset


class ProcessRequestDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveDestroyAPIView):
    """
    API endpoint representing a single process request.
    """

    model = ProcessRequest
    serializer_class = ProcessRequestDetailSerializer

    def delete(self, request, *args, **kwargs):
        process_request = ProcessRequest.objects.get(id=kwargs['pk'])
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

    model = ProcessRequest
    serializer_class = ProcessRequest

    def patch(self, request, *args, **kwargs):
        """
        Override patch for validation:
          - ensure user is a Worker
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
                process_request.assignment_date = datetime.datetime.now()
                process_request.save()

                # serialize the updated ProcessRequest
                serializer = ProcessRequestSerializer(process_request)

                return Response(serializer.data, status=201)
            except ValidationError as e:
                return Response(data={'detail': e.messages}, status=400)

        return Response(data={'detail': 'Bad request'}, status=400)


class ClusterList(
        LoginRequiredMixin,
        generics.ListCreateAPIView
    ):
    """
    API endpoint for listing and creating a Cluster.
    """
    model = Cluster
    serializer_class = ClusterSerializer
    filter_fields = ('process_request',)

    def post(self, request, *args, **kwargs):
        """
        Override post to ensure user is a worker.
        """
        if hasattr(self.request.user, 'worker'):
            try:
                worker = Worker.objects.get(user=self.request.user)
                process_request = ProcessRequest.objects.get(
                    id=request.DATA['process_request'])
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
        queryset=ProcessRequest.objects.all(),
        name='cluster__process_request'
    )
    cluster_index = django_filters.ModelMultipleChoiceFilter(
        queryset=Cluster.objects.all(),
        name='cluster__cluster_index'
    )
    label_name = django_filters.ModelMultipleChoiceFilter(
        queryset=CellSubsetLabel.objects.all(),
        name='label__name'
    )

    class Meta:
        model = ClusterLabel
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

    model = ClusterLabel
    serializer_class = ClusterLabelSerializer
    filter_class = ClusterLabelFilter

    def get_queryset(self):
        """
        Results are restricted to projects to which the user belongs.
        """

        user_projects = Project.objects.get_projects_user_can_view(
            self.request.user)
        queryset = ClusterLabel.objects.filter(
            label__project__in=user_projects
        )

        return queryset

    def post(self, request, *args, **kwargs):
        label = get_object_or_404(
            CellSubsetLabel, id=request.DATA['label']
        )
        cluster = get_object_or_404(
            Cluster, id=request.DATA['cluster']
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

    model = ClusterLabel
    serializer_class = ClusterLabelSerializer

    def delete(self, request, *args, **kwargs):
        cluster_label = ClusterLabel.objects.get(id=kwargs['pk'])
        if not cluster_label.label.project.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(ClusterLabelDetail, self).delete(request, *args, **kwargs)


class SampleClusterFilter(django_filters.FilterSet):
    process_request = django_filters.ModelMultipleChoiceFilter(
        queryset=ProcessRequest.objects.all(),
        name='cluster__process_request'
    )
    cluster_index = django_filters.ModelMultipleChoiceFilter(
        queryset=Cluster.objects.all(),
        name='cluster__cluster_index'
    )

    class Meta:
        model = SampleCluster
        fields = [
            'process_request',
            'cluster',
            'cluster_index',
            'sample'
        ]


class SampleClusterList(
        LoginRequiredMixin,
        generics.ListCreateAPIView
    ):
    """
    API endpoint for listing and creating a SampleCluster.
    """
    model = SampleCluster
    serializer_class = SampleClusterSerializer
    filter_class = SampleClusterFilter

    def post(self, request, *args, **kwargs):
        """
        Override post to ensure user is a worker and matches the
        ProcessRequest and save all relations in an atomic transaction
        """
        if hasattr(self.request.user, 'worker'):
            try:
                worker = Worker.objects.get(user=self.request.user)
                cluster = Cluster.objects.get(id=request.DATA['cluster_id'])
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
            sample = Sample.objects.get(id=request.DATA['sample_id'])

            with transaction.atomic():
                sample_cluster = SampleCluster(
                    cluster=cluster,
                    sample=sample,
                )

                # save event indices in a numpy file
                events_file = TemporaryFile()
                np.savetxt(
                    events_file,
                    np.array(request.DATA['events']),
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
                for param in request.DATA['parameters']:
                    SampleClusterParameter.objects.create(
                        sample_cluster=sample_cluster,
                        channel=param,
                        location=request.DATA['parameters'][param]
                    )

                # Finally, save all the SampleClusterComponent instances
                # along with their parameters
                for comp in request.DATA['components']:
                    scc = SampleClusterComponent.objects.create(
                        sample_cluster=sample_cluster,
                        covariance_matrix=comp['covariance'],
                        weight=comp['weight']
                    )
                    for comp_param in comp['parameters']:
                        SampleClusterComponentParameter.objects.create(
                            sample_cluster_component=scc,
                            channel=comp_param,
                            location=comp['parameters'][comp_param]
                        )

        except Exception as e:  # catch any exception to rollback changes
            return Response(data={'detail': e.message}, status=400)

        serializer = SampleClusterSerializer(
            sample_cluster,
            context={'request': request}
        )
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class SampleClusterComponentFilter(django_filters.FilterSet):
    process_request = django_filters.ModelMultipleChoiceFilter(
        queryset=ProcessRequest.objects.all(),
        name='sample_cluster__cluster__process_request'
    )
    sample = django_filters.ModelMultipleChoiceFilter(
        queryset=Sample.objects.all(),
        name='sample_cluster__sample'
    )
    cluster = django_filters.ModelMultipleChoiceFilter(
        queryset=Cluster.objects.all(),
        name='sample_cluster__cluster'
    )

    class Meta:
        model = SampleCluster
        fields = [
            'process_request',
            'sample',
            'cluster'
        ]


class SampleClusterComponentList(
        LoginRequiredMixin,
        generics.ListAPIView
    ):
    """
    API endpoint for listing and creating a SampleCluster.
    """
    model = SampleCluster
    serializer_class = SampleClusterSerializer
    filter_class = SampleClusterFilter
