from django.conf.urls import url
from django.views.generic import TemplateView

from repository.api_utils import repository_api_root
from repository.api_views import *
from repository.api_views_process_request import *
from repository.views import reflow_app, permission_denied

# Override handler403 to provide a custom permission denied page.
# Otherwise, a user has no links to get to their resources
# Esp. useful for 'next' redirection after login
handler403 = TemplateView.as_view(template_name='403.html')

# API routes
urlpatterns = [
    url(r'^api/repository/?$', repository_api_root, name='repository-api-root'),

    url(r'^api/repository/permissions/?$', PermissionList.as_view(), name='permission-list'),
    url(r'^api/repository/permissions/(?P<pk>\d+)/?$', PermissionDetail.as_view(), name='permission-detail'),
    url(r'^api/repository/users/?$', UserList.as_view(), name='user-list'),
    url(r'^api/repository/users/(?P<pk>\d+)/?$', UserDetail.as_view(), name='user-detail'),
    url(r'^api/repository/user/?$', get_user_details, name='get_user_details'),
    url(r'^api/repository/user/change_password/?$', change_user_password, name='change_user_password'),
    url(r'^api/repository/user/(?P<username>\w+)/?$', is_user, name='is_user'),

    url(r'^api/repository/markers/?$', MarkerList.as_view(), name='marker-list'),
    url(r'^api/repository/markers/(?P<pk>\d+)/?$', MarkerDetail.as_view(), name='marker-detail'),
    url(r'^api/repository/fluorochromes/?$', FluorochromeList.as_view(), name='fluorochrome-list'),
    url(r'^api/repository/fluorochromes/(?P<pk>\d+)/?$', FluorochromeDetail.as_view(), name='fluorochrome-detail'),
    url(r'^api/repository/specimens/?$', SpecimenList.as_view(), name='specimen-list'),
    url(r'^api/repository/specimens/(?P<pk>\d+)/?$', SpecimenDetail.as_view(), name='specimen-detail'),
    url(r'^api/repository/parameter_functions/?$', get_parameter_functions, name='get_parameter_functions'),
    url(r'^api/repository/parameter_value_types/?$', get_parameter_value_types,
        name='get_parameter_value_types'),

    url(r'^api/repository/projects/?$', ProjectList.as_view(), name='project-list'),
    url(r'^api/repository/projects/(?P<pk>\d+)/?$', ProjectDetail.as_view(), name='project-detail'),
    url(r'^api/repository/projects/(?P<project>\d+)/permissions/?$', get_project_permissions, name='get-project-permissions'),
    url(r'^api/repository/projects/(?P<pk>\d+)/sites_by_permission/?$', ProjectSitesByPermissionList.as_view(), name='project-sites-by-permission-list'),
    url(r'^api/repository/projects/(?P<pk>\d+)/users/?$', ProjectUserDetail.as_view(), name='project-user-detail'),
    url(r'^api/repository/panel_templates/?$', PanelTemplateList.as_view(), name='panel-template-list'),
    url(r'^api/repository/panel_templates/(?P<pk>\d+)/?$', PanelTemplateDetail.as_view(), name='panel-template-detail'),
    url(r'^api/repository/panel_variants/?$', PanelVariantList.as_view(), name='panel-variant-list'),
    url(r'^api/repository/panel_variants/(?P<pk>\d+)/?$', PanelVariantDetail.as_view(), name='panel-variant-detail'),
    url(r'^api/repository/cell_subset_labels/?$', CellSubsetLabelList.as_view(), name='cell-subset-label-list'),
    url(r'^api/repository/cell_subset_labels/(?P<pk>\d+)/?$', CellSubsetLabelDetail.as_view(), name='cell-subset-label-detail'),

    url(r'^api/repository/sites/?$', SiteList.as_view(), name='site-list'),
    url(r'^api/repository/sites/(?P<pk>\d+)/?$', SiteDetail.as_view(), name='site-detail'),
    url(r'^api/repository/sites/(?P<site>\d+)/permissions/?$', get_site_permissions, name='get-site-permissions'),
    url(r'^api/repository/site_panels/?$', SitePanelList.as_view(), name='site-panel-list'),
    url(r'^api/repository/site_panels/(?P<pk>\d+)/?$', SitePanelDetail.as_view(), name='site-panel-detail'),

    url(r'^api/repository/subject_groups/?$', SubjectGroupList.as_view(), name='subject-group-list'),
    url(r'^api/repository/subject_groups/(?P<pk>\d+)/?$', SubjectGroupDetail.as_view(), name='subject-group-detail'),
    url(r'^api/repository/subjects/?$', SubjectList.as_view(), name='subject-list'),
    url(r'^api/repository/subjects/(?P<pk>\d+)/?$', SubjectDetail.as_view(), name='subject-detail'),

    url(r'^api/repository/visit_types/?$', VisitTypeList.as_view(), name='visit-type-list'),
    url(r'^api/repository/visit_types/(?P<pk>\d+)/?$', VisitTypeDetail.as_view(), name='visittype-detail'),

    url(r'^api/repository/stimulations/?$', StimulationList.as_view(), name='stimulation-list'),
    url(r'^api/repository/stimulations/(?P<pk>\d+)/?$', StimulationDetail.as_view(), name='stimulation-detail'),

    url(r'^api/repository/samples/?$', SampleList.as_view(), name='sample-list'),
    url(r'^api/repository/samples/add/?$', CreateSample.as_view(), name='create-sample'),
    url(r'^api/repository/samples/(?P<pk>\d+)/?$', SampleDetail.as_view(), name='sample-detail'),
    url(r'^api/repository/samples/(?P<pk>\d+)/fcs_original/?$', retrieve_sample, name='retrieve_sample'),
    url(r'^api/repository/samples/(?P<pk>\d+)/fcs/?$', retrieve_sample_as_pk, name='sample-download-as-pk'),
    url(r'^api/repository/samples/(?P<pk>\d+)/fcs_clean/?$', retrieve_clean_sample, name='retrieve_clean_sample'),

    url(r'^api/repository/samplemetadata/?$', SampleMetaDataList.as_view(), name='sample-metadata-list'),

    url(r'^api/repository/sample_collections/?$', SampleCollectionList.as_view(), name='sample-collection-list'),
    url(r'^api/repository/sample_collections/(?P<pk>\d+)/?$', SampleCollectionDetail.as_view(), name='sample-collection-detail'),
    url(r'^api/repository/sample_collection_members/?$', SampleCollectionMemberList.as_view(), name='sample-collection-member-list'),

    url(r'^api/repository/compensations/?$', CompensationList.as_view(), name='compensation-list'),
    url(r'^api/repository/compensations/(?P<pk>\d+)/?$', CompensationDetail.as_view(), name='compensation-detail'),
    url(r'^api/repository/compensations/(?P<pk>\d+)/csv/?$', retrieve_compensation_as_csv, name='retrieve_compensation_as_csv'),
    url(r'^api/repository/compensations/(?P<pk>\d+)/object/?$', retrieve_compensation_as_csv_object, name='retrieve_compensation_as_csv_object'),
    url(r'^api/repository/compensations/(?P<pk>\d+)/npy/?$', retrieve_compensation_as_numpy, name='retrieve_compensation_as_numpy'),

    url(r'^api/repository/workers/(?P<pk>\d+)/?$', WorkerDetail.as_view(), name='worker-detail'),
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
    url(r'^api/repository/process_requests/stage2/?$', ProcessRequestStage2Create.as_view(), name='process-request-stage2-create'),
    url(r'^api/repository/process_requests/(?P<pk>\d+)/request_assignment/?$', ProcessRequestAssignmentUpdate.as_view(), name='process-request-assignment'),
    url(r'^api/repository/process_requests/(?P<pk>\d+)/report_error/?$', ProcessRequestReportError.as_view(), name='process-request-report-error'),
    url(r'^api/repository/process_requests/(?P<pk>\d+)/revoke_assignment/?$', revoke_process_request_assignment, name='revoke-process-request-assignment'),
    url(r'^api/repository/process_requests/(?P<pk>\d+)/verify_assignment/?$', verify_process_request_assignment, name='verify-process-request-assignment'),
    url(r'^api/repository/process_requests/(?P<pk>\d+)/complete_assignment/?$', complete_process_request_assignment, name='complete-process-request-assignment'),
    url(r'^api/repository/clusters/?$', ClusterList.as_view(), name='cluster-list'),
    url(r'^api/repository/cluster_labels/?$', ClusterLabelList.as_view(), name='cluster-label-list'),
    url(r'^api/repository/cluster_labels/(?P<pk>\d+)/?$', ClusterLabelDetail.as_view(), name='cluster-label-detail'),
    url(r'^api/repository/sample_clusters/?$', SampleClusterList.as_view(), name='sample-cluster-list'),
    url(r'^api/repository/sample_clusters/(?P<pk>\d+)/csv/?$', retrieve_sample_cluster_events, name='retrieve_sample_cluster_events'),
    url(r'^api/repository/sample_cluster_components/?$', SampleClusterComponentList.as_view(), name='sample-cluster-component-list'),

    # Non-API routes
    url(r'^403$', permission_denied, name='permission_denied'),
    url(r'^warning$', TemplateView.as_view(template_name='warning.html'), name='warning_page'),
    url(r'^$', reflow_app, name='home')
]