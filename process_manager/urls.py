from django.conf.urls import patterns, url

from process_manager.api_views import *

# API routes
urlpatterns = patterns('process_manager.api_views',
    url(r'^api/process_manager/$', 'process_manager_api_root', name='process-manager-api-root'),
    url(r'^api/process_manager/processes/$', ProcessList.as_view(), name='process-list'),
    url(r'^api/process_manager/workers/$', WorkerList.as_view(), name='worker-list'),
    url(r'^api/process_manager/verify_worker/$', verify_worker, name='verify-worker'),
    url(r'^api/process_manager/process_requests/$', ProcessRequestList.as_view(), name='process-request-list'),
    url(r'^api/process_manager/viable_process_requests/$', ViableProcessRequestList.as_view(), name='viable-process-request-list'),
    url(r'^api/process_manager/process_requests/(?P<pk>\d+)/$', ProcessRequestDetail.as_view(), name='process-request-detail'),
    url(r'^api/process_manager/process_requests/(?P<pk>\d+)/request_assignment/$', ProcessRequestAssignmentUpdate.as_view(), name='process-request-assignment'),
    url(r'^api/process_manager/process_requests/(?P<pk>\d+)/revoke_assignment/$', revoke_process_request_assignment, name='revoke-process-request-assignment'),
    url(r'^api/process_manager/process_requests/(?P<pk>\d+)/verify_assignment/$', verify_process_request_assignment, name='verify-process-request-assignment'),
)


# Regular web routes
urlpatterns += patterns('process_manager.views',
    url(r'^process_manager/$', 'process_dashboard', name='process_dashboard'),
    url(r'^process_manager/process/(?P<process_id>\d+)/$', 'view_process', name='view_process'),
    url(r'^process_manager/process/add/$', 'add_process', name='add_process'),
    url(r'^process_manager/process/(?P<process_id>\d+)/input/add/$', 'add_process_input', name='add_process_input'),
    url(r'^process_manager/process_input/(?P<process_input_id>\d+)/edit/$', 'edit_process_input', name='edit_process_input'),
    url(r'^process_manager/worker/(?P<worker_id>\d+)/$', 'view_worker', name='view_worker'),
    url(r'^process_manager/worker/add/$', 'add_worker', name='add_worker'),
    url(r'^process_manager/worker/(?P<worker_id>\d+)/register_process$', 'register_process_to_worker', name='register_process_to_worker'),
    url(r'^process_manager/process_requests/(?P<process_request_id>\d+)/$', 'view_process_request', name='view_process_request'),
    url(r'^process_manager/process/(?P<process_id>\d+)/request/create/$', 'create_process_request', name='create_process_request'),
)