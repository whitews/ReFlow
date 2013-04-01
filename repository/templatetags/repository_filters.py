__author__ = 'swhite'

from repository.models import Project

from django import template
from django.contrib.auth.models import User

register = template.Library()


@register.filter
def user_projects(value):
    if User.objects.filter(username=value).count() == 0:
        return None

    return Project.objects.get_user_projects(user=User.objects.get(username=value))