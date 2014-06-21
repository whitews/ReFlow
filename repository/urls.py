from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from repository.api_views import *

# Override handler403 to provide a custom permission denied page.
# Otherwise, a user has no links to get to their resources
# Esp. useful for 'next' redirection after login
handler403 = TemplateView.as_view(template_name='403.html')

# API routes
urlpatterns = patterns('repository.api_views',
    url(r'^api/repository/?$', 'repository_api_root', name='repository-api-root'),

    url(r'^api/repository/markers/?$', MarkerList.as_view(), name='marker-list'),
    url(r'^api/repository/fluorochromes/?$', FluorochromeList.as_view(), name='fluorochrome-list'),
    url(r'^api/repository/specimens/?$', SpecimenList.as_view(), name='specimen-list'),
    url(r'^api/repository/parameter_functions/?$', get_parameter_functions, name='get_parameter_functions'),
    url(r'^api/repository/parameter_value_types/?$', get_parameter_value_types,
        name='get_parameter_value_types'),

    url(r'^api/repository/projects/?$', ProjectList.as_view(), name='project-list'),
    url(r'^api/repository/projects/(?P<pk>\d+)/?$', ProjectDetail.as_view(), name='project-detail'),
    url(r'^api/repository/projects/(?P<project>\d+)/permissions/?$', get_project_permissions, name='get-project-permissions'),
    url(r'^api/repository/project_panels/?$', ProjectPanelList.as_view(), name='project-panel-list'),
    url(r'^api/repository/project_panels/(?P<pk>\d+)/?$', ProjectPanelDetail.as_view(), name='project-panel-detail'),

    url(r'^api/repository/sites/?$', SiteList.as_view(), name='site-list'),
    url(r'^api/repository/sites/(?P<pk>\d+)/?$', SiteDetail.as_view(), name='site-detail'),
    url(r'^api/repository/sites/(?P<site>\d+)/permissions/?$', get_site_permissions, name='get-site-permissions'),
    url(r'^api/repository/site_panels/?$', SitePanelList.as_view(), name='site-panel-list'),
    url(r'^api/repository/site_panels/(?P<pk>\d+)/?$', SitePanelDetail.as_view(), name='site-panel-detail'),
    url(r'^api/repository/cytometers/?$', CytometerList.as_view(), name='cytometer-list'),
    url(r'^api/repository/cytometers/(?P<pk>\d+)/?$', CytometerDetail.as_view(), name='cytometer-detail'),

    url(r'^api/repository/subject_groups/?$', SubjectGroupList.as_view(), name='subject-group-list'),
    url(r'^api/repository/subjects/?$', SubjectList.as_view(), name='subject-list'),
    url(r'^api/repository/subjects/(?P<pk>\d+)/?$', SubjectDetail.as_view(), name='subject-detail'),

    url(r'^api/repository/visit_types/?$', VisitTypeList.as_view(), name='visit-type-list'),
    url(r'^api/repository/visit_types/(?P<pk>\d+)/?$', VisitTypeDetail.as_view(), name='visittype-detail'),

    url(r'^api/repository/stimulations/?$', StimulationList.as_view(), name='stimulation-list'),
    url(r'^api/repository/stimulations/(?P<pk>\d+)/?$', StimulationDetail.as_view(), name='stimulation-detail'),

    url(r'^api/repository/samples/?$', SampleList.as_view(), name='sample-list'),
    url(r'^api/repository/samples/add/?$', CreateSampleList.as_view(), name='create-sample-list'),
    url(r'^api/repository/samples/(?P<pk>\d+)/?$', SampleDetail.as_view(), name='sample-detail'),
    url(r'^api/repository/samples/(?P<pk>\d+)/fcs_original/?$', retrieve_sample, name='retrieve_sample'),
    url(r'^api/repository/samples/(?P<pk>\d+)/fcs/?$', retrieve_sample_as_pk, name='sample-download-as-pk'),
    url(r'^api/repository/samples/(?P<pk>\d+)/csv/?$', retrieve_subsample_as_csv, name='retrieve_subsample_as_csv'),
    url(r'^api/repository/samples/(?P<pk>\d+)/npy/?$', retrieve_subsample_as_numpy, name='retrieve_subsample_as_numpy'),

    url(r'^api/repository/samplemetadata/?$', SampleMetaDataList.as_view(), name='sample-metadata-list'),

    url(r'^api/repository/sample_collections/?$', SampleCollectionList.as_view(), name='sample-collection-list'),
    url(r'^api/repository/sample_collections/(?P<pk>\d+)/?$', SampleCollectionDetail.as_view(), name='sample-collection-detail'),
    url(r'^api/repository/sample_collection_members/?$', SampleCollectionMemberList.as_view(), name='sample-collection-member-list'),

    url(r'^api/repository/beads/?$', BeadList.as_view(), name='bead-list'),
    url(r'^api/repository/beads/add/?$', CreateBeadList.as_view(), name='create-bead-list'),
    url(r'^api/repository/beads/(?P<pk>\d+)/?$', BeadDetail.as_view(), name='bead-detail'),
    url(r'^api/repository/beads/(?P<pk>\d+)/fcs_original/?$', retrieve_bead_sample, name='retrieve_bead_sample'),
    url(r'^api/repository/beads/(?P<pk>\d+)/fcs/?$', retrieve_bead_sample_as_pk, name='bead-download-as-pk'),
    url(r'^api/repository/beads/(?P<pk>\d+)/csv/?$', retrieve_bead_subsample_as_csv, name='retrieve_bead_subsample_as_csv'),
    url(r'^api/repository/beads/(?P<pk>\d+)/npy/?$', retrieve_bead_subsample_as_numpy, name='retrieve_bead_subsample_as_numpy'),

    url(r'^api/repository/compensations/?$', CompensationList.as_view(), name='compensation-list'),
    url(r'^api/repository/compensations/add/?$', CreateCompensation.as_view(), name='create-compensation'),
    url(r'^api/repository/compensations/(?P<pk>\d+)/?$', CompensationDetail.as_view(), name='compensation-detail'),
    url(r'^api/repository/compensations/(?P<pk>\d+)/csv/?$', retrieve_compensation_as_csv, name='retrieve_compensation_as_csv'),
    url(r'^api/repository/compensations/(?P<pk>\d+)/npy/?$', retrieve_compensation_as_numpy, name='retrieve_compensation_as_numpy'),

    url(r'^api/repository/workers/?$', WorkerList.as_view(), name='worker-list'),
    url(r'^api/repository/subprocess_categories/?$', SubprocessCategoryList.as_view(), name='subprocess-category-list'),
    url(r'^api/repository/subprocess_implementations/?$', SubprocessImplementationList.as_view(), name='subprocess-implementation-list'),
    url(r'^api/repository/subprocess_inputs/?$', SubprocessInputList.as_view(), name='subprocess-input-list'),
    url(r'^api/repository/verify_worker/?$', verify_worker, name='verify-worker'),
    url(r'^api/repository/process_requests/?$', ProcessRequestList.as_view(), name='process-request-list'),
    url(r'^api/repository/process_request_inputs/?$', ProcessRequestInputList.as_view(), name='process-request-input-list'),
    url(r'^api/repository/viable_process_requests/?$', ViableProcessRequestList.as_view(), name='viable-process-request-list'),
    url(r'^api/repository/assigned_process_requests/?$', AssignedProcessRequestList.as_view(), name='assigned-process-request-list'),
    url(r'^api/repository/process_requests/(?P<pk>\d+)/?$', ProcessRequestDetail.as_view(), name='process-request-detail'),
    url(r'^api/repository/process_requests/(?P<pk>\d+)/request_assignment/?$', ProcessRequestAssignmentUpdate.as_view(), name='process-request-assignment'),
    url(r'^api/repository/process_requests/(?P<pk>\d+)/revoke_assignment/?$', revoke_process_request_assignment, name='revoke-process-request-assignment'),
    url(r'^api/repository/process_requests/(?P<pk>\d+)/verify_assignment/?$', verify_process_request_assignment, name='verify-process-request-assignment'),
    url(r'^api/repository/process_requests/(?P<pk>\d+)/complete_assignment/?$', complete_process_request_assignment, name='complete-process-request-assignment'),
    url(r'^api/repository/process_request_outputs/add/?$', CreateProcessRequestOutput.as_view(), name='create-process-request-output'),
    url(r'^api/repository/process_request_outputs/(?P<pk>\d+)/download/?$', retrieve_process_request_output_value, name='retrieve_process_request_output'),
)

# Angular web routes
urlpatterns += patterns('repository.views',
    url(r'^$', 'reflow_app', name='home'),
    url(r'^beads/upload/$', 'bead_upload_app', name='bead_upload_app'),
    url(r'^processing/request/$', 'process_request_app', name='process_request_app'),
    url(r'^panel_templates/$', 'panel_template_app', name='panel_template_app'),
)

# Regular web routes
urlpatterns += patterns('repository.views',
    url(r'^403$', 'permission_denied', name='permission_denied'),
    url(r'^reflow_admin/$', 'admin', name='admin'),

    url(r'^markers/$', 'view_markers', name='view_markers'),
    url(r'^markers/add/$', 'add_marker', name='add_marker'),
    url(r'^markers/(?P<marker_id>\d+)/edit/$', 'add_marker', name='edit_marker'),

    url(r'^fluorochromes/$', 'view_fluorochromes', name='view_fluorochromes'),
    url(r'^fluorochromes/add/$', 'add_fluorochrome', name='add_fluorochrome'),
    url(r'^fluorochromes/(?P<fluorochrome_id>\d+)/edit/$', 'add_fluorochrome', name='edit_fluorochrome'),

    url(r'^specimens/$', 'view_specimens', name='view_specimens'),
    url(r'^specimens/add/$', 'add_specimen', name='add_specimen'),
    url(r'^specimens/(?P<specimen_id>\d+)/edit/$', 'edit_specimen', name='edit_specimen'),

    url(r'^project/add/$', 'add_project', name='add_project'),
    url(r'^project/(?P<project_id>\d+)/edit/$', 'add_project', name='edit_project'),

    url(r'^project/(?P<project_id>\d+)/users/$', 'view_project_users', name='view_project_users'),
    url(r'^project/(?P<project_id>\d+)/users/add/$', 'add_user_permissions', name='add_user_permissions'),
    url(r'^project/(?P<project_id>\d+)/users/(?P<user_id>-?\d+)/manage/$', 'manage_project_user', name='manage_project_user'),
    url(r'^site/(?P<site_id>\d+)/users/(?P<user_id>-?\d+)/manage/$', 'manage_site_user', name='manage_site_user'),

    url(r'^project/(?P<project_id>\d+)/stimulations/add/$', 'add_stimulation', name='add_stimulation'),
    url(r'^project/(?P<project_id>\d+)/stimulations/(?P<stimulation_id>\d+)/edit/$', 'add_stimulation', name='edit_stimulation'),

    url(r'^project/(?P<project_id>\d+)/templates/$', 'view_project_panels', name='view_project_panels'),
    url(r'^project/(?P<project_id>\d+)/templates/(?P<panel_id>\d+)/copy/$', 'copy_project_panel', name='copy_project_panel'),

    url(r'^project/(?P<project_id>\d+)/sites/add/$', 'add_site', name='add_site'),
    url(r'^site/(?P<site_id>\d+)/edit/$', 'edit_site', name='edit_site'),

    url(r'^project/(?P<project_id>\d+)/cytometers/add/$', 'add_cytometer', name='add_cytometer'),
    url(r'^project/(?P<project_id>\d+)/cytometers/(?P<cytometer_id>\d+)/edit/$', 'add_cytometer', name='edit_cytometer'),

    url(r'^project/(?P<project_id>\d+)/compensations/$', 'view_compensations', name='project_compensations'),
    url(r'^project/(?P<project_id>\d+)/compensations/add/$', 'add_compensation', name='add_compensation'),
    url(r'^project/(?P<project_id>\d+)/compensations/(?P<compensation_id>\d+)/edit/$', 'add_compensation', name='edit_compensation'),

    url(r'^project/(?P<project_id>\d+)/visit_types/add/$', 'add_visit_type', name='add_visit_type'),
    url(r'^visit_types/(?P<visit_type_id>\d+)/edit/$', 'edit_visit_type', name='edit_visit_type'),

    url(r'^project/(?P<project_id>\d+)/subject_groups/add/$', 'add_subject_group', name='add_subject_group'),
    url(r'^project/(?P<project_id>\d+)/subject_groups/(?P<subject_group_id>\d+)/edit/$', 'edit_subject_group', name='edit_subject_group'),

    url(r'^project/(?P<project_id>\d+)/subjects/add/$', 'add_subject', name='add_subject'),
    url(r'^subject/(?P<subject_id>\d+)/edit/$', 'edit_subject', name='edit_subject'),

    url(r'^project/(?P<project_id>\d+)/samples/$', 'view_samples', name='view_project_samples'),
    url(r'^sample/(?P<sample_id>\d+)/edit/$', 'edit_sample', name='edit_sample'),
    url(r'^sample/(?P<sample_id>\d+)/parameters/$', 'render_sample_parameters', name='render_sample_parameters'),
    url(r'^sample/(?P<sample_id>\d+)/compensation/$', 'render_sample_compensation', name='render_sample_compensation'),

    url(r'^project/(?P<project_id>\d+)/beads/$', 'view_beads', name='view_beads'),

    url(r'^warning$', TemplateView.as_view(template_name='warning.html'), name='warning_page'),

    url(r'^processing/dashboard/$', 'process_dashboard', name='process_dashboard'),
    url(r'^processing/worker/add/$', 'add_worker', name='add_worker'),
    url(r'^processing/process_requests/(?P<process_request_id>\d+)/$', 'view_process_request', name='view_process_request'),
)