from django.conf.urls import patterns, url

__author__ = 'swhite'

urlpatterns = patterns('authenticate.views',
    url(r'^login/$', 'login_view', name="login"),
    url(r'^logout/$', 'logout_view', name="logout"),
    url(r'^login_failed/$', 'login_failed', name="login_failed"),
)
