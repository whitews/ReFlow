from django.conf.urls import include, url
from django.contrib import admin
admin.autodiscover()
from api_views import api_root
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_docs.views import documentation

urlpatterns = [
    url(r'^', include('authenticate.urls')),
    url(r'^', include('repository.urls')),
    # (r'^admin/', include(admin.site.urls)),
    url(r'^api/$', api_root),
    url(r'^api/token-auth/$', obtain_auth_token, name='api-token-auth'),
    url(r'^api/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/docs/', include('rest_framework_docs.urls', namespace='rest_framework_docs')),
    url(r'^api/docs/$', documentation, name='api-docs')
]
