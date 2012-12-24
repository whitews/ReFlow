__author__ = 'swhite'

from repository.models import ProjectUserMap

from django import template
from django.contrib.auth.models import User

register = template.Library()

@register.filter
def user_projects(value):
    if User.objects.filter(username=value).count() == 0:
        return None

    return ProjectUserMap.objects.get_user_projects(user=User.objects.get(username=value))