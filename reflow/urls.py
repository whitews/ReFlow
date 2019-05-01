from django.conf.urls import include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^', include('authenticate.urls')),
    url(r'^', include('repository.urls')),
    # (r'^admin/', include(admin.site.urls)),
    url(r'^api/$', 'reflow.api_views.api_root'),
    url(r'^api/token-auth/$', 'rest_framework.authtoken.views.obtain_auth_token', name='api-token-auth'),
    url(r'^api/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/docs/', include('rest_framework_docs.urls', namespace='rest_framework_docs')),
    url(r'^api/docs/$', 'rest_framework_docs.views.documentation', name='api-docs')
]
