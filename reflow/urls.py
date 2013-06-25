from django.conf.urls import patterns, include

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^', include('authenticate.urls')),
    (r'^api/', include('rest_framework.urls', namespace='rest_framework')),
    (r'^rest-api/', include('rest_framework_docs.urls', namespace='rest_framework_docs')),
    (r'^', include('repository.urls')),
    (r'^', include('process_manager.urls')),
    (r'^admin/', include(admin.site.urls)),
)
