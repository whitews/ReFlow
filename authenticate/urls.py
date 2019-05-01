from django.conf.urls import url

__author__ = 'swhite'

urlpatterns = [
    url(r'^login/?$', 'authenticate.views.login_view', name="login"),
    url(r'^logout/?$', 'authenticate.views.logout_view', name="logout"),
    url(r'^login_failed/?$', 'authenticate.views.login_failed', name="login_failed")
]
