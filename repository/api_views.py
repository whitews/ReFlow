from rest_framework import generics
from rest_framework import status
from rest_framework.authentication import \
    SessionAuthentication, \
    TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.decorators import api_view
from rest_framework.response import Response

import django_filters

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, \
    MultipleObjectsReturned, ValidationError
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from guardian.models import UserObjectPermission
from guardian.shortcuts import assign_perm, remove_perm

import datetime
import re

from repository import models
from repository import serializers
from repository import controllers
from repository.api_utils import LoginRequiredMixin, PermissionRequiredMixin

# Design Note: For any detail view the PermissionRequiredMixin will
# restrict access to users of that project
# For any List view, the view itself will have to restrict the list
# of objects by user


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
        user_id = int(request.data['user_id'])
        current_password = request.data['current_password']
        new_password = request.data['new_password']
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
    project = get_object_or_404(models.Project, pk=project)

    if not (request.user in project.get_project_users() or
            request.user.is_superuser):
        raise PermissionDenied

    perms = project.get_user_permissions(request.user)

    return Response({'permissions': perms})


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def get_site_permissions(request, site):
    site = get_object_or_404(models.Site, pk=site)

    if not site.has_view_permission(request.user):
        raise PermissionDenied

    perms = site.get_user_permissions(request.user)

    return Response({'permissions': perms})


@api_view(['GET'])
def get_parameter_functions(request):
    return Response(models.PARAMETER_TYPE_CHOICES)


@api_view(['GET'])
def get_parameter_value_types(request):
    return Response(models.PARAMETER_VALUE_TYPE_CHOICES)


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def retrieve_sample(request, pk):
    sample = get_object_or_404(models.Sample, pk=pk)

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
    sample = get_object_or_404(models.Sample, pk=pk)

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
def retrieve_clean_sample(request, pk):
    sample = get_object_or_404(models.Sample, pk=pk)

    if not sample.has_view_permission(request.user):
        raise PermissionDenied
    file_name = "_".join([
        sample.site_panel.site.site_name,
        sample.subject.subject_code,
        sample.site_panel.panel_template.panel_name,
        str(sample.acquisition_date)
    ])
    clean_file = sample.get_clean_fcs()
    response = HttpResponse(
        clean_file,
        content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s' \
        % file_name + '.fcs'
    return response


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def retrieve_subsample_as_csv(request, pk):
    sample = get_object_or_404(models.Sample, pk=pk)

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
    sample = get_object_or_404(models.Sample, pk=pk)

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
    compensation = get_object_or_404(models.Compensation, pk=pk)

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
    compensation = get_object_or_404(models.Compensation, pk=pk)

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
    compensation = get_object_or_404(models.Compensation, pk=pk)

    if not compensation.has_view_permission(request.user):
        raise PermissionDenied

    response = HttpResponse(
        compensation.compensation_file.file,
        content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s' \
        % "comp_" + str(compensation.id) + '.npy'
    return response


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
    serializer_class = serializers.PermissionSerializer

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
    serializer_class = serializers.PermissionSerializer
    filter_class = PermissionFilter

    def get_queryset(self):
        """
        Override .get_queryset() to filter permissions related to projects
        for which the requesting user has user management permissions.
        """

        # get list of project IDs the user has user management privileges for
        projects = models.Project.objects.get_projects_user_can_manage_users(
            self.request.user).values_list('id', flat=True)

        # get list of sites for those projects
        sites = models.Site.objects.filter(project__in=projects)\
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
        if request.data['model'] == 'project':
            project = models.Project.objects.get(id=request.data['object_pk'])
            if request.data['permission_codename'] not in project_perms:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            obj = project
        elif request.data['model'] == 'site':
            try:
                obj = models.Site.objects.get(id=request.data['object_pk'])
                project = obj.project
            except ObjectDoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            if request.data['permission_codename'] not in site_perms:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # verify user is valid
        try:
            user = User.objects.get(username=request.data['username'])
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # ensure requesting user has user management permission for this project
        if not project.has_user_management_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        # save the permission
        assign_perm(
            request.data['permission_codename'],
            user,
            obj
        )

        perm = UserObjectPermission.objects.get(
            user=user,
            object_pk=obj.id,
            permission__codename=request.data['permission_codename']
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
    serializer_class = serializers.UserSerializer

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

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                # check for optional properties
                user_kwargs = {}
                if 'first_name' in serializer.validated_data:
                    user_kwargs['first_name'] = serializer.validated_data[
                        'first_name'
                    ]
                if 'last_name' in serializer.validated_data:
                    user_kwargs['last_name'] = serializer.validated_data[
                        'last_name'
                    ]

                # different calls needed for regular vs super users
                is_superuser = False
                if 'is_superuser' in serializer.validated_data:
                    if serializer.validated_data['is_superuser']:
                        is_superuser = True

                if is_superuser:
                    User.objects.create_superuser(
                        serializer.validated_data['username'],
                        email=serializer.validated_data['email'],
                        password=serializer.validated_data['password'],
                        **user_kwargs
                    )
                else:
                    User.objects.create_user(
                        serializer.validated_data['username'],
                        email=serializer.validated_data['email'],
                        password=serializer.validated_data['password'],
                        **user_kwargs
                    )
            except IntegrityError, e:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            except Exception, e:
                # TODO: remove this after more experimentation
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class UserDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint representing a single ReFlow user.
    """

    model = User
    serializer_class = serializers.UserSerializer

    def put(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)

        user = User.objects.get(id=kwargs['pk'])
        # don't allow editing workers
        if hasattr(user, 'worker'):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Only allow editing certain User attributes,
        # and calling super put oddly resets user's date_joined & last_login
        # We don't want that, so we'll have to save the user ourselves,
        # But the fun doesn't stop there! This ends up a little messy
        # b/c you can't set model instance attributes as strings like a
        # dictionary can, so we need to set them each explicitly, then save
        try:
            if 'username' in request.data:
                user.username = request.data['username']
            if 'email' in request.data:
                user.email = request.data['email']
            if 'first_name' in request.data:
                user.first_name = request.data['first_name']
            if 'last_name' in request.data:
                user.last_name = request.data['last_name']
            if 'is_active' in request.data:
                user.is_active = request.data['is_active']
            if 'is_superuser' in request.data:
                user.is_superuser = request.data['is_superuser']
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

    model = models.Project
    serializer_class = serializers.ProjectSerializer
    filter_fields = ('project_name',)

    def get_queryset(self):
        """
        Override .get_queryset() to filter on user's projects.
        """
        queryset = models.Project.objects.get_projects_user_can_view(
            self.request.user
        )
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

    model = models.Project
    serializer_class = serializers.ProjectSerializer

    def put(self, request, *args, **kwargs):
        project = models.Project.objects.get(id=kwargs['pk'])
        if not project.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(ProjectDetail, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        project = models.Project.objects.get(id=kwargs['pk'])
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

    model = models.Project
    serializer_class = serializers.ProjectUserSerializer

    def get(self, request, *args, **kwargs):
        project = models.Project.objects.get(id=kwargs['pk'])

        if not project.has_user_management_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(ProjectUserDetail, self).get(request, *args, **kwargs)
        return response


class ProjectSitesByPermissionList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of project sites with the specified
    permission.
    """

    model = models.Site
    serializer_class = serializers.SiteSerializer

    def get_queryset(self):
        project = models.Project.objects.get(id=self.kwargs['pk'])

        queryset = []

        if 'permission' in self.request.query_params:
            if 'add_site_data' in self.request.query_params['permission']:
                queryset = models.Site.objects.get_sites_user_can_add(
                    self.request.user,
                    project
                )
            elif 'modify_site_data' in self.request.query_params['permission']:
                queryset = models.Site.objects.get_sites_user_can_modify(
                    self.request.user,
                    project
                )
        return queryset


class CellSubsetLabelList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint representing a list of cell subset labels.
    """

    model = models.CellSubsetLabel
    serializer_class = serializers.CellSubsetLabelSerializer
    filter_fields = ('project', 'name',)

    def get_queryset(self):
        """
        Results are restricted to projects to which the user belongs.
        """

        user_projects = models.Project.objects.get_projects_user_can_view(
            self.request.user)
        queryset = models.CellSubsetLabel.objects.filter(
            project__in=user_projects
        )

        return queryset

    def post(self, request, *args, **kwargs):
        project = models.Project.objects.get(id=request.data['project'])
        if not project.has_add_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(CellSubsetLabelList, self).post(
            request,
            *args,
            **kwargs
        )
        return response


class CellSubsetLabelDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint representing a single cell subset label.
    """

    model = models.CellSubsetLabel
    serializer_class = serializers.CellSubsetLabelSerializer

    def put(self, request, *args, **kwargs):
        subset_label = models.CellSubsetLabel.objects.get(id=kwargs['pk'])
        if not subset_label.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(CellSubsetLabelDetail, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        subset_label = models.CellSubsetLabel.objects.get(id=kwargs['pk'])
        if not subset_label.project.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(CellSubsetLabelDetail, self).delete(
            request,
            *args,
            **kwargs
        )


class VisitTypeList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint representing a list of panels.
    """

    model = models.VisitType
    serializer_class = serializers.VisitTypeSerializer
    filter_fields = ('visit_type_name', 'project')

    def get_queryset(self):
        """
        Override .get_queryset() to restrict panels to projects
        to which the user belongs.
        """

        user_projects = models.Project.objects.get_projects_user_can_view(
            self.request.user)

        # filter on user's projects
        queryset = models.VisitType.objects.filter(project__in=user_projects)

        return queryset

    def post(self, request, *args, **kwargs):
        project = models.Project.objects.get(id=request.data['project'])
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

    model = models.VisitType
    serializer_class = serializers.VisitTypeSerializer

    def put(self, request, *args, **kwargs):
        visit_type = models.VisitType.objects.get(id=kwargs['pk'])
        if not visit_type.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(VisitTypeDetail, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        visit_type = models.VisitType.objects.get(id=kwargs['pk'])
        if not visit_type.project.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(VisitTypeDetail, self).delete(request, *args, **kwargs)


class SubjectGroupList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint representing a list of subject groups.
    """

    model = models.SubjectGroup
    serializer_class = serializers.SubjectGroupSerializer
    filter_fields = ('group_name', 'project')

    def get_queryset(self):
        """
        Override .get_queryset() to restrict subject groups to projects
        to which the user belongs.
        """

        user_projects = models.Project.objects.get_projects_user_can_view(
            self.request.user)

        # filter on user's projects
        queryset = models.SubjectGroup.objects.filter(project__in=user_projects)

        return queryset

    def post(self, request, *args, **kwargs):
        project = models.Project.objects.get(id=request.data['project'])
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

    model = models.SubjectGroup
    serializer_class = serializers.SubjectGroupSerializer

    def put(self, request, *args, **kwargs):
        subject_group = models.SubjectGroup.objects.get(id=kwargs['pk'])
        if not subject_group.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(SubjectGroupDetail, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        subject_group = models.SubjectGroup.objects.get(id=kwargs['pk'])
        if not subject_group.project.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(SubjectGroupDetail, self).delete(request, *args, **kwargs)


class SubjectList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint representing a list of subjects.
    """

    model = models.Subject
    serializer_class = serializers.SubjectSerializer
    filter_fields = ('subject_code', 'project', 'subject_group')

    def get_queryset(self):
        """
        Override .get_queryset() to restrict panels to projects
        to which the user belongs.
        """

        user_projects = models.Project.objects.get_projects_user_can_view(
            self.request.user)

        # filter on user's projects
        queryset = models.Subject.objects.filter(project__in=user_projects)

        return queryset

    def post(self, request, *args, **kwargs):
        project = models.Project.objects.get(id=request.data['project'])
        if not project.has_add_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        # Verify project for both subject and subject group matches
        if 'subject_group' in request.data:
            subject_group = models.SubjectGroup.objects.get(
                id=request.data['subject_group']
            )
            if subject_group.project_id != project.id:
                raise ValidationError("Group chosen is not in this Project")

        response = super(SubjectList, self).post(request, *args, **kwargs)
        return response


class SubjectDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint representing a single subject.
    """

    model = models.Subject
    serializer_class = serializers.SubjectSerializer

    def put(self, request, *args, **kwargs):
        subject = models.Subject.objects.get(id=kwargs['pk'])
        if not subject.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(SubjectDetail, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        subject = models.Subject.objects.get(id=kwargs['pk'])
        if not subject.project.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(SubjectDetail, self).delete(request, *args, **kwargs)


class PanelTemplateFilter(django_filters.FilterSet):
    project = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Project.objects.all(),
        name='project')

    class Meta:
        model = models.PanelTemplate
        fields = [
            'project',
            'panel_name'
        ]


class PanelTemplateList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint representing a list of panel templates.
    """

    model = models.PanelTemplate
    serializer_class = serializers.PanelTemplateSerializer
    filter_class = PanelTemplateFilter

    def get_queryset(self):
        """
        Restrict panel templates to projects for which
        the user has view permission.
        """
        user_projects = models.Project.objects.get_projects_user_can_view(
            self.request.user)

        # filter on user's projects
        queryset = models.PanelTemplate.objects.filter(
            project__in=user_projects
        )

        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data

        # validate all the template components
        errors = controllers.validate_panel_template_request(data, request.user)
        if len(errors) > 0:
            return Response(data=errors, status=400)

        # we can create the PanelTemplate instance now, but we'll do so inside
        # an atomic transaction
        try:
            project = models.Project.objects.get(id=data['project'])

            with transaction.atomic():
                panel_template = models.PanelTemplate(
                    project=project,
                    panel_name=data['panel_name'],
                    panel_description=data['panel_description']
                )
                panel_template.save()

                for param in data['parameters']:
                    if param['fluorochrome']:
                        param_fluoro = models.Fluorochrome.objects.get(
                            id=param['fluorochrome'])
                    else:
                        param_fluoro = None

                    ppp = models.PanelTemplateParameter.objects.create(
                        panel_template=panel_template,
                        parameter_type=param['parameter_type'],
                        parameter_value_type=param['parameter_value_type'],
                        fluorochrome=param_fluoro
                    )
                    for marker in param['markers']:
                        models.PanelTemplateParameterMarker.objects.create(
                            panel_template_parameter=ppp,
                            marker=models.Marker.objects.get(id=marker)
                        )

                # by default, every panel template gets a full stain variant
                models.PanelVariant.objects.create(
                    panel_template=panel_template,
                    staining_type='FULL'
                )

        except Exception as e:  # catch any exception to rollback changes
            if hasattr(e, 'messages'):
                return Response(data={'detail': e.messages}, status=400)
            return Response(data={'detail': e.message}, status=400)

        serializer = serializers.PanelTemplateSerializer(
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

    model = models.PanelTemplate
    serializer_class = serializers.PanelTemplateSerializer

    def put(self, request, *args, **kwargs):
        data = request.data

        # first, check if template has any site panels, editing templates
        # with existing site panels is not allowed
        panel_template = models.PanelTemplate.objects.get(id=kwargs['pk'])
        if panel_template.sitepanel_set.count() > 0:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # validate all the template components
        errors = controllers.validate_panel_template_request(data, request.user)
        if len(errors) > 0:
            return Response(data=errors, status=400)

        # we can create the PanelTemplate instance now, but we'll do so inside
        # an atomic transaction
        try:
            project = models.Project.objects.get(id=data['project'])

            with transaction.atomic():
                panel_template.project = project
                panel_template.panel_name = data['panel_name']
                panel_template.panel_description = data['panel_description']
                panel_template.save()

                panel_template.paneltemplateparameter_set.all().delete()

                for param in data['parameters']:
                    if param['fluorochrome']:
                        param_fluoro = models.Fluorochrome.objects.get(
                            id=param['fluorochrome'])
                    else:
                        param_fluoro = None

                    ppp = models.PanelTemplateParameter.objects.create(
                        panel_template=panel_template,
                        parameter_type=param['parameter_type'],
                        parameter_value_type=param['parameter_value_type'],
                        fluorochrome=param_fluoro
                    )
                    for marker in param['markers']:
                        models.PanelTemplateParameterMarker.objects.create(
                            panel_template_parameter=ppp,
                            marker=models.Marker.objects.get(id=marker)
                        )
        except Exception as e:  # catch any exception to rollback changes
            return Response(data={'detail': e.message}, status=400)

        serializer = serializers.PanelTemplateSerializer(
            panel_template,
            context={'request': request}
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        panel_template = models.PanelTemplate.objects.get(id=kwargs['pk'])
        if not panel_template.project.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(PanelTemplateDetail, self).delete(request, *args, **kwargs)


class PanelVariantList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint representing a list of panel variants.
    """

    model = models.PanelVariant
    serializer_class = serializers.PanelVariantSerializer
    filter_fields = ('panel_template', 'staining_type', 'name')

    def get_queryset(self):
        """
        Override .get_queryset() to restrict panels to projects
        to which the user belongs.
        """

        user_projects = models.Project.objects.get_projects_user_can_view(
            self.request.user)

        # filter on user's projects
        queryset = models.PanelVariant.objects.filter(
            panel_template__project__in=user_projects
        )

        return queryset

    def post(self, request, *args, **kwargs):
        panel_template = models.PanelTemplate.objects.get(
            id=request.data['panel_template']
        )
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

    model = models.PanelVariant
    serializer_class = serializers.PanelVariantSerializer

    def put(self, request, *args, **kwargs):
        panel_variant = models.PanelVariant.objects.get(id=kwargs['pk'])
        project = panel_variant.panel_template.project
        if not project.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(PanelVariantDetail, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        panel_variant = models.PanelVariant.objects.get(id=kwargs['pk'])
        project = panel_variant.panel_template.project
        if not project.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(PanelVariantDetail, self).delete(request, *args, **kwargs)


class SiteList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint representing a list of sites.
    """

    model = models.Site
    serializer_class = serializers.SiteSerializer
    filter_fields = ('site_name', 'project')

    def get_queryset(self):
        """
        Override .get_queryset() to restrict sites for which
        the user has view permission.
        """
        queryset = models.Site.objects.get_sites_user_can_view(
            self.request.user
        )

        return queryset

    def post(self, request, *args, **kwargs):
        project = models.Project.objects.get(id=request.data['project'])
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

    model = models.Site
    serializer_class = serializers.SiteSerializer

    def put(self, request, *args, **kwargs):
        site = models.Site.objects.get(id=kwargs['pk'])
        if not site.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(SiteDetail, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        site = models.Site.objects.get(id=kwargs['pk'])
        if not site.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(SiteDetail, self).delete(request, *args, **kwargs)


class SitePanelFilter(django_filters.FilterSet):
    panel_template = django_filters.ModelMultipleChoiceFilter(
        queryset=models.PanelTemplate.objects.all(),
        name='panel_template')
    site = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Site.objects.all(),
        name='site')
    project = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Project.objects.all(),
        name='panel_template__project')
    fluorochrome = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Fluorochrome.objects.all(),
        name='sitepanelparameter__fluorochrome'
    )
    fluorochrome_abbreviation = django_filters.CharFilter(
        name='sitepanelparameter__fluorochrome__fluorochrome_abbreviation'
    )

    class Meta:
        model = models.SitePanel
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

    model = models.SitePanel
    serializer_class = serializers.SitePanelSerializer
    filter_class = SitePanelFilter

    def get_queryset(self):
        """
        Override .get_queryset() to restrict panels to sites
        to which the user belongs.
        """

        user_sites = models.Site.objects.get_sites_user_can_view(
            self.request.user
        )

        # need to filter by multiple IDs but django-filter doesn't seem to like
        # that, so we'll do it ourselves here

        # filter on user's projects
        queryset = models.SitePanel.objects.filter(site__in=user_sites)

        id_value = self.request.query_params.get('id', None)
        if id_value:
            id_list = id_value.split(',')
            queryset = queryset.filter(id__in=id_list)

        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data

        # validate all the site panel components
        errors = controllers.validate_site_panel_request(data, request.user)
        if len(errors) > 0:
            return Response(data=errors, status=400)

        # we can create the SitePanel instance now, but we'll do so inside
        # an atomic transaction
        try:
            site = models.Site.objects.get(id=data['site'])
            panel_template = models.PanelTemplate.objects.get(
                id=data['panel_template']
            )

            with transaction.atomic():
                site_panel = models.SitePanel(
                    site=site,
                    panel_template=panel_template,
                    site_panel_comments=data['site_panel_comments']
                )
                site_panel.save()

                for param in data['parameters']:
                    if param['parameter_type'] == 'NUL':
                        param['parameter_value_type'] = 'N'
                        param['fluorochrome'] = None
                        param['markers'] = []

                    if param['fluorochrome']:
                        param_fluoro = models.Fluorochrome.objects.get(
                            id=param['fluorochrome'])
                    else:
                        param_fluoro = None

                    spp = models.SitePanelParameter.objects.create(
                        site_panel=site_panel,
                        parameter_type=param['parameter_type'],
                        parameter_value_type=param['parameter_value_type'],
                        fluorochrome=param_fluoro,
                        fcs_number=param['fcs_number'],
                        fcs_text=param['fcs_text'],
                        fcs_opt_text=param['fcs_opt_text']
                    )
                    for marker in param['markers']:
                        models.SitePanelParameterMarker.objects.create(
                            site_panel_parameter=spp,
                            marker=models.Marker.objects.get(id=marker)
                        )
        except Exception as e:  # catch any exception to rollback changes
            return Response(data={'detail': e.message}, status=400)

        serializer = serializers.SitePanelSerializer(
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

    model = models.SitePanel
    serializer_class = serializers.SitePanelSerializer

    def delete(self, request, *args, **kwargs):
        site_panel = models.SitePanel.objects.get(id=kwargs['pk'])
        if not site_panel.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(SitePanelDetail, self).delete(request, *args, **kwargs)


class CytometerFilter(django_filters.FilterSet):

    site = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Site.objects.all(),
        name='site')
    site_name = django_filters.MultipleChoiceFilter(
        choices=models.Site.objects.all().values_list('site_name', 'id'),
        name='site__site_name')
    project = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Project.objects.all(),
        name='site__project')

    class Meta:
        model = models.Cytometer
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

    model = models.Cytometer
    serializer_class = serializers.CytometerSerializer
    filter_class = CytometerFilter

    def get_queryset(self):
        """
        Override .get_queryset() to restrict panels to sites
        to which the user belongs.
        """

        user_sites = models.Site.objects.get_sites_user_can_view(
            self.request.user
        )

        # filter on user's projects
        queryset = models.Cytometer.objects.filter(site__in=user_sites)

        return queryset

    def post(self, request, *args, **kwargs):
        site = models.Site.objects.get(id=request.data['site'])
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

    model = models.Cytometer
    serializer_class = serializers.CytometerSerializer

    def put(self, request, *args, **kwargs):
        cytometer = models.Cytometer.objects.get(id=kwargs['pk'])
        if not cytometer.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(CytometerDetail, self).put(request, *args, **kwargs)
        return response

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        cytometer = models.Cytometer.objects.get(id=kwargs['pk'])
        if not cytometer.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(CytometerDetail, self).delete(request, *args, **kwargs)


class MarkerList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint representing a list of markers.
    """

    model = models.Marker
    serializer_class = serializers.MarkerSerializer
    filter_fields = ('project', 'marker_abbreviation')

    def get_queryset(self):
        """
        Results are restricted to projects to which the user belongs.
        """

        user_projects = models.Project.objects.get_projects_user_can_view(
            self.request.user)
        queryset = models.Marker.objects.filter(project__in=user_projects)

        return queryset

    def post(self, request, *args, **kwargs):
        project = models.Project.objects.get(id=request.data['project'])
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

    model = models.Marker
    serializer_class = serializers.MarkerSerializer

    def put(self, request, *args, **kwargs):
        try:
            marker = models.Marker.objects.get(id=kwargs['pk'])
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
            marker = models.Marker.objects.get(id=kwargs['pk'])
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

    model = models.Fluorochrome
    serializer_class = serializers.FluorochromeSerializer
    filter_fields = ('project', 'fluorochrome_abbreviation')

    def get_queryset(self):
        """
        Results are restricted to projects to which the user belongs.
        """

        user_projects = models.Project.objects.get_projects_user_can_view(
            self.request.user)
        queryset = models.Fluorochrome.objects.filter(project__in=user_projects)

        return queryset

    def post(self, request, *args, **kwargs):
        project = models.Project.objects.get(id=request.data['project'])
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

    model = models.Fluorochrome
    serializer_class = serializers.FluorochromeSerializer

    def put(self, request, *args, **kwargs):
        try:
            fluorochrome = models.Fluorochrome.objects.get(id=kwargs['pk'])
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
            fluorochrome = models.Fluorochrome.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not fluorochrome.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        if fluorochrome.sitepanelparameter_set.count() > 0:
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(FluorochromeDetail, self).delete(
            request,
            *args,
            **kwargs
        )
        return response


class SpecimenList(LoginRequiredMixin, generics.ListCreateAPIView):
    """
    API endpoint representing a list of specimen types.
    """

    model = models.Specimen
    serializer_class = serializers.SpecimenSerializer
    filter_fields = ('specimen_name',)
    queryset = models.Specimen.objects.all()

    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = super(SpecimenList, self).post(request, *args, **kwargs)
        return response


class SpecimenDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint representing a single fluorochrome.
    """

    model = models.Specimen
    serializer_class = serializers.SpecimenSerializer

    def put(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            models.Specimen.objects.get(id=kwargs['pk'])
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
            specimen = models.Specimen.objects.get(id=kwargs['pk'])
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

    model = models.Stimulation
    serializer_class = serializers.StimulationSerializer
    filter_fields = ('project', 'stimulation_name',)

    def get_queryset(self):
        """
        Results are restricted to projects to which the user belongs.
        """

        user_projects = models.Project.objects.get_projects_user_can_view(
            self.request.user)
        queryset = models.Stimulation.objects.filter(project__in=user_projects)

        return queryset

    def post(self, request, *args, **kwargs):
        project = models.Project.objects.get(id=request.data['project'])
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

    model = models.Stimulation
    serializer_class = serializers.StimulationSerializer

    def put(self, request, *args, **kwargs):
        stimulation = models.Stimulation.objects.get(id=kwargs['pk'])
        if not stimulation.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(StimulationDetail, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        stimulation = models.Stimulation.objects.get(id=kwargs['pk'])
        if not stimulation.project.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(StimulationDetail, self).delete(request, *args, **kwargs)


class CreateSample(LoginRequiredMixin, generics.CreateAPIView):
    """
    API endpoint for creating a new Sample.
    """

    model = models.Sample
    serializer_class = serializers.SamplePOSTSerializer

    def create(self, request, *args, **kwargs):
        """
        Override create b/c we need to call Sample.clean() and DRF create
        doesn't call the model's clean method
        """

        site_panel = models.SitePanel.objects.get(id=request.data['site_panel'])
        site = models.Site.objects.get(id=site_panel.site_id)
        if not site.has_add_permission(request.user):
            raise PermissionDenied

        try:
            with transaction.atomic():
                sample = models.Sample(
                    acquisition_date=datetime.datetime.strptime(
                        request.data['acquisition_date'],
                        "%Y-%m-%d"
                    ).date(),
                    subject_id=request.data['subject'],
                    visit_id=request.data['visit'],
                    cytometer_id=request.data['cytometer'],
                    panel_variant_id=request.data['panel_variant'],
                    site_panel_id=request.data['site_panel'],
                    pretreatment=request.data['pretreatment'],
                    storage=request.data['storage'],
                    specimen_id=request.data['specimen'],
                    stimulation_id=request.data['stimulation'],
                    sample_file=request.data['sample_file']
                )
                sample.clean()
                sample.save()
        except Exception as e:  # catch any exception to rollback changes
            return Response(data={'detail': e.message}, status=400)

        serializer = serializers.SamplePOSTSerializer(
            sample,
            context={'request': request}
        )
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class SampleFilter(django_filters.FilterSet):
    panel = django_filters.ModelMultipleChoiceFilter(
        queryset=models.PanelTemplate.objects.all(),
        name='site_panel__panel_template')
    project = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Project.objects.all(),
        name='site_panel__panel_template__project')
    site = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Site.objects.all(),
        name='site_panel__site')
    panel_variant = django_filters.ModelMultipleChoiceFilter(
        queryset=models.PanelVariant.objects.all())
    site_panel = django_filters.ModelMultipleChoiceFilter(
        queryset=models.SitePanel.objects.all())
    cytometer = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Cytometer.objects.all(),
        name='cytometer')
    subject = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Subject.objects.all())
    subject_group = django_filters.ModelMultipleChoiceFilter(
        queryset=models.SubjectGroup.objects.all(),
        name='subject__subject_group')
    subject_code = django_filters.CharFilter(
        name='subject__subject_code')
    visit = django_filters.ModelMultipleChoiceFilter(
        queryset=models.VisitType.objects.all(),
        name='visit')
    specimen = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Specimen.objects.all(),
        name='specimen')
    stimulation = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Stimulation.objects.all(),
        name='stimulation')
    original_filename = django_filters.CharFilter(lookup_type="icontains")

    class Meta:
        model = models.Sample
        fields = [
            'acquisition_date',
            'sha1'
        ]


class SampleList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of samples.
    """

    model = models.Sample
    serializer_class = serializers.SampleSerializer
    filter_class = SampleFilter

    def get_queryset(self):
        """
        Results are restricted to projects to which the user belongs.
        """

        user_sites = models.Site.objects.get_sites_user_can_view(
            self.request.user
        )
        queryset = models.Sample.objects.filter(
            site_panel__site__in=user_sites)

        return queryset


class SampleDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint representing a single FCS sample.
    """

    model = models.Sample
    serializer_class = serializers.SampleSerializer

    def put(self, request, *args, **kwargs):
        sample = models.Sample.objects.get(id=request.data['id'])
        if not sample.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(SampleDetail, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, *args, **kwargs):
        sample = models.Sample.objects.get(id=kwargs['pk'])
        if not sample.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(SampleDetail, self).delete(request, *args, **kwargs)


class SampleMetaDataList(LoginRequiredMixin, generics.ListAPIView):
    """
    API endpoint representing a list of sample metadata.
    """

    model = models.SampleMetadata
    serializer_class = serializers.SampleMetadataSerializer
    filter_fields = ('id', 'sample', 'key', 'value')

    def get_queryset(self):
        """
        Override .get_queryset() to restrict sites for which
        the user has view permission.
        """
        user_sites = models.Site.objects.get_sites_user_can_view(
            self.request.user
        )
        queryset = models.SampleMetadata.objects.filter(
            sample__site_panel__site__in=user_sites)

        return queryset


class CompensationFilter(django_filters.FilterSet):

    site = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Site.objects.all(),
        name='site_panel__site')
    site_panel = django_filters.ModelMultipleChoiceFilter(
        queryset=models.SitePanel.objects.all(),
        name='site_panel')
    project = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Project.objects.all(),
        name='site_panel__site__project')

    class Meta:
        model = models.Compensation
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

    model = models.Compensation
    serializer_class = serializers.CompensationSerializer
    filter_class = CompensationFilter

    def get_queryset(self):
        """
        Override .get_queryset() to restrict panels to projects
        to which the user belongs.
        """
        user_sites = models.Site.objects.get_sites_user_can_view(
            self.request.user
        )

        # filter on user's sites
        queryset = models.Compensation.objects.filter(
            site_panel__site__in=user_sites)
        return queryset

    def create(self, request, *args, **kwargs):
        """
        Override post to ensure user has permission to add data to the site.
        """
        matrix_text = request.data['matrix_text'].splitlines(False)
        if not len(matrix_text) > 1:
            raise ValidationError("Too few rows.")

        # first row should be headers matching the PnN value (fcs_text field)
        # may be tab or comma delimited
        # (spaces can't be delimiters b/c they are allowed in the PnN value)
        pnn_list = re.split('\t|,\s*', matrix_text[0])
        site_panel = None
        if 'site_panel' in request.data:
            site_panel_candidate = get_object_or_404(
                models.SitePanel,
                id=request.data['site_panel']
            )
            site = site_panel_candidate.site
            if controllers.matches_site_panel_colors(
                    pnn_list, site_panel_candidate):
                site_panel = site_panel_candidate

        if not site.has_add_permission(request.user):
            raise PermissionDenied

        try:
            comp = models.Compensation(
                site_panel_id=request.data['site_panel'],
                acquisition_date=datetime.datetime.strptime(
                    request.data['acquisition_date'],
                    "%Y-%m-%d"
                ).date(),
                name=request.data['name'],
                matrix_text=request.data['matrix_text']
            )
            comp.clean()
            comp.save()
        except Exception as e:
            return Response(data={'detail': e.message}, status=400)

        serializer = serializers.CompensationSerializer(
            comp,
            context={'request': request}
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class CompensationDetail(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generics.RetrieveDestroyAPIView):
    """
    API endpoint representing a single FCS sample.
    """

    model = models.Compensation
    serializer_class = serializers.CompensationSerializer

    def delete(self, request, *args, **kwargs):
        compensation = models.Compensation.objects.get(id=kwargs['pk'])
        if not compensation.has_modify_permission(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super(CompensationDetail, self).delete(request, *args, **kwargs)
