from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from repository.api_views import *

# Override handler403 to provide a custom permission denied page.
# Otherwise, a user has no links to get to their resources
# Esp. useful for 'next' redirection after login
handler403 = TemplateView.as_view(template_name='403.html')

# API routes
urlpatterns = patterns('repository.api_views',
    url(r'^api/repository/$', 'repository_api_root', name='repository-api-root'),
    url(r'^api/repository/specimens/$', SpecimenList.as_view(), name='specimen-list'),
    url(r'^api/repository/compensations/$', CompensationList.as_view(), name='compensation-list'),
    url(r'^api/repository/compensations/(?P<pk>\d+)/$', CompensationDetail.as_view(), name='compensation-detail'),
    url(r'^api/repository/project_panels/$', ProjectPanelList.as_view(), name='project-panel-list'),
    url(r'^api/repository/project_panels/(?P<pk>\d+)/$', ProjectPanelDetail.as_view(), name='project-panel-detail'),
    url(r'^api/repository/site_panels/$', SitePanelList.as_view(), name='site-panel-list'),
    url(r'^api/repository/site_panels/(?P<pk>\d+)/$', SitePanelDetail.as_view(), name='site-panel-detail'),
    url(r'^api/repository/parameters/$', ProjectPanelParameterList.as_view(), name='project-parameter-list'),
    url(r'^api/repository/project_panel_parameters/(?P<pk>\d+)/$', ProjectPanelParameterDetail.as_view(), name='project-parameter-detail'),
    url(r'^api/repository/projects/$', ProjectList.as_view(), name='project-list'),
    url(r'^api/repository/projects/(?P<pk>\d+)/$', ProjectDetail.as_view(), name='project-detail'),
    url(r'^api/repository/stimulations/$', StimulationList.as_view(), name='stimulation-list'),
    url(r'^api/repository/samples/$', SampleList.as_view(), name='sample-list'),
    url(r'^api/repository/samples/add/$', CreateSampleList.as_view(), name='create-sample-list'),
    url(r'^api/repository/samples/(?P<pk>\d+)/$', SampleDetail.as_view(), name='sample-detail'),
    url(r'^api/repository/samples/(?P<pk>\d+)/download/$', retrieve_sample, name='sample-download'),
    url(r'^api/repository/samples/(?P<pk>\d+)/apply_panel/$', SamplePanelUpdate.as_view(), name='sample-panel-update'),
    url(r'^api/repository/sample_sets/$', SampleSetList.as_view(), name='sample-set-list'),
    url(r'^api/repository/sample_sets/(?P<pk>\d+)/$', SampleSetDetail.as_view(), name='sample-set-detail'),
    url(r'^api/repository/sites/$', SiteList.as_view(), name='site-list'),
    url(r'^api/repository/sites/(?P<pk>\d+)/$', SiteDetail.as_view(), name='site-detail'),
    url(r'^api/repository/subject_groups/$', SubjectGroupList.as_view(), name='subject-group-list'),
    url(r'^api/repository/subjects/$', SubjectList.as_view(), name='subject-list'),
    url(r'^api/repository/subjects/(?P<pk>\d+)/$', SubjectDetail.as_view(), name='subject-detail'),
    url(r'^api/repository/visit_types/$', VisitTypeList.as_view(), name='visit-type-list'),
    url(r'^api/repository/visit_types/(?P<pk>\d+)/$', VisitTypeDetail.as_view(), name='visittype-detail'),
)

# Regular web routes
urlpatterns += patterns('repository.views',
    url(r'^403$', 'permission_denied', name='permission_denied'),
    url(r'^$', 'home', name='home'),
    url(r'^reflow_admin/$', 'admin', name='admin'),

    url(r'^antibodies/$', 'view_antibodies', name='view_antibodies'),
    url(r'^antibodies/add/$', 'add_antibody', name='add_antibody'),
    url(r'^antibodies/(?P<antibody_id>\d+)/edit/$', 'edit_antibody', name='edit_antibody'),

    url(r'^fluorochromes/$', 'view_fluorochromes', name='view_fluorochromes'),
    url(r'^fluorochromes/add/$', 'add_fluorochrome', name='add_fluorochrome'),
    url(r'^fluorochromes/(?P<fluorochrome_id>\d+)/edit/$', 'edit_fluorochrome', name='edit_fluorochrome'),

    url(r'^specimens/$', 'view_specimens', name='view_specimens'),
    url(r'^specimens/add/$', 'add_specimen', name='add_specimen'),
    url(r'^specimens/(?P<specimen_id>\d+)/edit/$', 'edit_specimen', name='edit_specimen'),

    url(r'^project/(?P<project_id>\d+)/$', 'view_project', name='view_project'),
    url(r'^project/add/$', 'add_project', name='add_project'),
    url(r'^project/(?P<project_id>\d+)/edit/$', 'edit_project', name='edit_project'),

    url(r'^project/(?P<project_id>\d+)/users/$', 'view_project_users', name='view_project_users'),
    url(r'^project/(?P<project_id>\d+)/users/add/$', 'add_user_permissions', name='add_user_permissions'),
    url(r'^project/(?P<project_id>\d+)/users/(?P<user_id>-?\d+)/manage/$', 'manage_project_user', name='manage_project_user'),
    url(r'^site/(?P<site_id>\d+)/users/(?P<user_id>-?\d+)/manage/$', 'manage_site_user', name='manage_site_user'),

    url(r'^project/(?P<project_id>\d+)/stimulations/$', 'view_project_stimulations', name='view_project_stimulations'),
    url(r'^project/(?P<project_id>\d+)/stimulations/add/$', 'add_stimulation', name='add_stimulation'),
    url(r'^stimulations/(?P<stimulation_id>\d+)/edit/$', 'edit_stimulation', name='edit_stimulation'),

    url(r'^project/(?P<project_id>\d+)/panels/$', 'view_project_panels', name='view_project_panels'),
    url(r'^project/(?P<project_id>\d+)/panels/add/$', 'add_project_panel', name='add_project_panel'),
    url(r'^panels/(?P<panel_id>\d+)/edit/$', 'edit_project_panel', name='edit_project_panel'),

    url(r'^project/(?P<project_id>\d+)/sites/$', 'view_project_sites', name='view_project_sites'),
    url(r'^project/(?P<project_id>\d+)/sites/add/$', 'add_site', name='add_site'),
    url(r'^site/(?P<site_id>\d+)/edit/$', 'edit_site', name='edit_site'),

    url(r'^project/(?P<project_id>\d+)/compensations/$', 'view_compensations', name='project_compensations'),
    url(r'^project/(?P<project_id>\d+)/compensations/add/$', 'add_compensation', name='add_compensation'),
    url(r'^download/compensation/(?P<compensation_id>\d+)$', 'retrieve_compensation', name='retrieve_compensation'),

    url(r'^project/(?P<project_id>\d+)/visit_types/$', 'view_visit_types', name='project_visit_types'),
    url(r'^project/(?P<project_id>\d+)/visit_types/add/$', 'add_visit_type', name='add_visit_type'),
    url(r'^visit_types/(?P<visit_type_id>\d+)/edit/$', 'edit_visit_type', name='edit_visit_type'),

    url(r'^project/(?P<project_id>\d+)/site_panels/$', 'view_project_site_panels', name='view_project_site_panels'),
    url(r'^project/(?P<project_id>\d+)/site_panels/add/$', 'add_project_site_panel', name='add_project_site_panel'),
    url(r'^project/(?P<project_id>\d+)/site_panels/process_site_panel_post/$', 'process_site_panel_post', name='process_site_panel_post'),
    url(r'^site_panel/(?P<panel_id>\d+)/edit/$', 'edit_site_panel', name='edit_site_panel'),
    url(r'^parameter/(?P<panel_parameter_id>\d+)/remove/$', 'remove_panel_parameter', name='remove_panel_parameter'),

    url(r'^project/(?P<project_id>\d+)/subject_groups/$', 'view_subject_groups', name='subject_groups'),
    url(r'^project/(?P<project_id>\d+)/subject_groups/add/$', 'add_subject_group', name='add_subject_group'),
    url(r'^project/(?P<project_id>\d+)/subject_groups/(?P<subject_group_id>\d+)/edit/$', 'edit_subject_group', name='edit_subject_group'),

    url(r'^project/(?P<project_id>\d+)/subjects/$', 'view_subjects', name='view_subjects'),
    url(r'^project/(?P<project_id>\d+)/subjects/add/$', 'add_subject', name='add_subject'),
    url(r'^subject/(?P<subject_id>\d+)/edit/$', 'edit_subject', name='edit_subject'),

    url(r'^project/(?P<project_id>\d+)/samples/$', 'view_samples', name='view_project_samples'),
    url(r'^project/(?P<project_id>\d+)/samples/add/$', 'add_sample', name='add_sample'),
    url(r'^sample/(?P<sample_id>\d+)/edit/$', 'edit_sample', name='edit_sample'),
    url(r'^sample/(?P<sample_id>\d+)/parameters/$', 'render_sample_parameters', name='render_sample_parameters'),
    url(r'^download/sample/(?P<sample_id>\d+)$', 'retrieve_sample', name='retrieve_sample'),

    url(r'^project/(?P<project_id>\d+)/sample_sets/$', 'view_project_sample_sets', name='view_project_sample_sets'),
    url(r'^project/(?P<project_id>\d+)/sample_sets/add/$', 'add_sample_set', name='add_sample_set'),

    url(r'^warning$', TemplateView.as_view(template_name='warning.html'), name='warning_page'),
)