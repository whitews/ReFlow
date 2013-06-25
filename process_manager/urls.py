from django.conf.urls import patterns, url


# Regular web routes
urlpatterns = patterns('process_manager.views',
    url(r'^process_manager/dashboard$', 'process_dashboard', name='process_dashboard'),
    url(r'^process_manager/process/(?P<pk>\d+)$', 'view_process', name='view_process'),
    url(r'^process_manager/process/add/$', 'add_process', name='add_process'),
)