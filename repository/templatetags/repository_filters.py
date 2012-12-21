__author__ = 'swhite'

from repository.models import ProjectUserMap

from django import template
from django.contrib.auth.models import User

register = template.Library()

@register.filter
def user_projects(value):
    return ProjectUserMap.objects.get_user_projects(user=User.objects.get(username=value))