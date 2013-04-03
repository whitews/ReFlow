__author__ = 'swhite'

from django import template

register = template.Library()


@register.filter
def get_user_project_permissions(project, user):
    try:
        perms = project.get_user_permissions(user)
    except:
        # See Django docs: filter functions shouldn't raise exceptions and should fail silently
        # https://docs.djangoproject.com/en/dev/howto/custom-template-tags/#writing-custom-template-filters
        return None

    return perms


@register.filter
def get_user_site_permissions(site, user):
    try:
        perms = site.get_user_permissions(user)
    except:
        # See Django docs: filter functions shouldn't raise exceptions and should fail silently
        # https://docs.djangoproject.com/en/dev/howto/custom-template-tags/#writing-custom-template-filters
        return None

    return perms
