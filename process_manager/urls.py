from django.conf.urls import patterns, url


# Regular web routes
urlpatterns = patterns('process_manager.views',
    url(r'^process_manager/$', 'process_dashboard', name='process_dashboard'),
    url(r'^process_manager/process/(?P<process_id>\d+)/$', 'view_process', name='view_process'),
    url(r'^process_manager/process/add/$', 'add_process', name='add_process'),
    url(r'^process_manager/process/(?P<process_id>\d+)/input/add/$', 'add_process_input', name='add_process_input'),
    url(r'^process_manager/process_input/(?P<process_input_id>\d+)/edit/$', 'edit_process_input', name='edit_process_input'),
    url(r'^process_manager/worker/(?P<worker_id>\d+)/$', 'view_worker', name='view_worker'),
    url(r'^process_manager/worker/add/$', 'add_worker', name='add_worker'),
    url(r'^process_manager/worker/(?P<worker_id>\d+)/register_process$', 'register_process_to_worker', name='register_process_to_worker'),
    url(r'^process_manager/process_requests/$', 'process_requests', name='process_requests'),
    url(r'^process_manager/process/(?P<process_id>\d+)/request/create/$', 'create_process_request', name='create_process_request'),
)