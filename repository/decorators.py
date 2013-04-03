from repository.models import Project

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404


def require_project_or_site_view_permission(orig_func):
    def user_test(request, *args, **kwargs):
        if 'project_id' in kwargs:
            project = get_object_or_404(Project, pk=kwargs['project_id'])
        elif 'site_id' in kwargs:
            project = get_object_or_404(Project, site__pk=kwargs['site_id'])
        else:
            raise PermissionDenied

        # get_user_projects returns projects for any level of view access, even to a single site
        user_projects = Project.objects.get_user_projects(request.user)
        if not project in user_projects:
            raise PermissionDenied

        return orig_func(request, *args, **kwargs)

    return user_test


def require_project_user(orig_func):

    def user_test(request, *args, **kwargs):

        if 'project_id' in kwargs:
            project = get_object_or_404(Project, pk=kwargs['project_id'])
        elif 'site_id' in kwargs:
            project = get_object_or_404(Project, site__pk=kwargs['site_id'])
        elif 'visit_type_id' in kwargs:
            project = get_object_or_404(Project, projectvisittype__pk=kwargs['visit_type_id'])
        elif 'panel_id' in kwargs:
            project = get_object_or_404(Project, site__panel__pk=kwargs['panel_id'])
        elif 'subject_id' in kwargs:
            project = get_object_or_404(Project, subject__pk=kwargs['subject_id'])
        elif 'sample_id' in kwargs:
            project = get_object_or_404(Project, subject__sample__pk=kwargs['sample_id'])
        elif 'panel_parameter_id' in kwargs:
            project = get_object_or_404(Project, site__panel__panelparametermap__pk=kwargs['panel_parameter_id'])
        elif 'compensation_id' in kwargs:
            project = get_object_or_404(Project, site__compensation__pk=kwargs['compensation_id'])
        else:
            raise PermissionDenied

        if not project.has_view_permission(request.user):
            raise PermissionDenied

        return orig_func(request, *args, **kwargs)

    return user_test