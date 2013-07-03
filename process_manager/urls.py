from django.conf.urls import patterns, url


# Regular web routes
urlpatterns = patterns('process_manager.views',
    url(r'^process_manager/dashboard/$', 'process_dashboard', name='process_dashboard'),
    url(r'^process_manager/process/(?P<process_id>\d+)/$', 'view_process', name='view_process'),
    url(r'^process_manager/process/add/$', 'add_process', name='add_process'),
    url(r'^process_manager/process/(?P<process_id>\d+)/input/add$', 'add_process_input', name='add_process_input'),
)