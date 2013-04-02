__author__ = 'swhite'

from repository.models import Project

from django import template
from django.contrib.auth.models import User

register = template.Library()


@register.filter
def get_user_permissions(project, user):
    try:
        perms = project.get_user_permissions(user)
    except:
        return None

    return perms