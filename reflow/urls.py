from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^', include('authenticate.urls')),
    (r'^', include('repository.urls')),
    (r'^admin/', include(admin.site.urls)),
)

# Base REST API routes
urlpatterns += patterns('reflow.api_views',
    url(r'^api/$', 'api_root'),
)

urlpatterns += patterns('rest_framework',
    url(r'^api/token-auth/$', 'authtoken.views.obtain_auth_token', name='api-token-auth'),
)

urlpatterns += patterns('',
    (r'^api/', include('rest_framework.urls', namespace='rest_framework')),
    (r'^api/docs/', include('rest_framework_docs.urls', namespace='rest_framework_docs')),
    url(r'^api/docs/$', 'rest_framework_docs.views.documentation', name='api-docs')
)