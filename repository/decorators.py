from repository.models import Project, ProjectUserMap

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404


def require_project_user(orig_func):

    def user_test(request, *args, **kwargs):

        if 'project_id' in kwargs:
            project = get_object_or_404(Project, pk=kwargs['project_id'])
        elif 'site_id' in kwargs:
            project = get_object_or_404(Project, site__pk=kwargs['site_id'])
        elif 'panel_id' in kwargs:
            project = get_object_or_404(Project, site__panel__pk=kwargs['panel_id'])
        elif 'subject_id' in kwargs:
            project = get_object_or_404(Project, subject__pk=kwargs['subject_id'])
        elif 'sample_id' in kwargs:
            project = get_object_or_404(Project, subject__sample__pk=kwargs['sample_id'])
        elif 'panel_parameter_id' in kwargs:
            project = get_object_or_404(Project, site__panel__panelparametermap__pk=kwargs['panel_parameter_id'])
        else:
            raise PermissionDenied

        if not ProjectUserMap.objects.is_project_user(project, request.user):
            raise PermissionDenied

        return orig_func(request, *args, **kwargs)

    return user_test