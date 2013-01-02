__author__ = 'swhite'

from repository.models import Project, ProjectUserMap

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

def require_project_user(orig_func):

    def user_test(request, *args, **kwargs):

        if 'project_id' in kwargs:
            project = get_object_or_404(Project, pk=kwargs['project_id'])
            if not ProjectUserMap.objects.is_project_user(project, request.user):
                raise PermissionDenied
        else:
            raise PermissionDenied

        return orig_func(request, *args, **kwargs)

    return user_test