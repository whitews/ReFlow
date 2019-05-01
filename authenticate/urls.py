from django.conf.urls import url
from authenticate.views import login_view, logout_view, login_failed

__author__ = 'swhite'

urlpatterns = [
    url(r'^login/?$', login_view, name="login"),
    url(r'^logout/?$', logout_view, name="logout"),
    url(r'^login_failed/?$', login_failed, name="login_failed")
]
