from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from repository.api_views import *

# Override handler403 to provide a custom permission denied page.
# Otherwise, a user has no links to get to their resources
# Esp. useful for 'next' redirection after login
handler403 = TemplateView.as_view(template_name='403.html')

# API routes
urlpatterns = patterns('repository.api_views',
    url(r'^api/$', 'api_root'),
    url(r'^api/specimens/$', SpecimenList.as_view(), name='specimen-list'),
    url(r'^api/compensations/$', CompensationList.as_view(), name='compensation-list'),
    url(r'^api/compensations/(?P<pk>\d+)/$', CompensationDetail.as_view(), name='compensation-detail'),
    url(r'^api/panels/$', PanelList.as_view(), name='panel-list'),
    url(r'^api/panels/(?P<pk>\d+)/$', PanelDetail.as_view(), name='panel-detail'),
    url(r'^api/parameters/$', ParameterList.as_view(), name='parameter-list'),
    url(r'^api/parameters/(?P<pk>\d+)/$', ParameterDetail.as_view(), name='parameter-detail'),
    url(r'^api/projects/$', ProjectList.as_view(), name='project-list'),
    url(r'^api/projects/(?P<pk>\d+)/$', ProjectDetail.as_view(), name='project-detail'),
    url(r'^api/sample_groups/$', SampleGroupList.as_view(), name='sample-group-list'),
    url(r'^api/samples/$', SampleList.as_view(), name='sample-list'),
    url(r'^api/samples/add/$', CreateSampleList.as_view(), name='create-sample-list'),
    url(r'^api/samples/uncategorized/$', UncategorizedSampleList.as_view(), name='uncat-sample-list'),
    url(r'^api/samples/(?P<pk>\d+)/$', SampleDetail.as_view(), name='sample-detail'),
    url(r'^api/samples/(?P<pk>\d+)/download/$', retrieve_sample, name='sample-download'),
    url(r'^api/samples/(?P<pk>\d+)/apply_panel/$', SamplePanelUpdate.as_view(), name='sample-panel-update'),
    url(r'^api/samples/(?P<pk>\d+)/add_compensation/$', SampleCompensationCreate.as_view(), name='sample-compensation-create'),
    url(r'^api/sites/$', SiteList.as_view(), name='site-list'),
    url(r'^api/sites/(?P<pk>\d+)/$', SiteDetail.as_view(), name='site-detail'),
    url(r'^api/subject_groups/$', SubjectGroupList.as_view(), name='subject-group-list'),
    url(r'^api/subjects/$', SubjectList.as_view(), name='subject-list'),
    url(r'^api/subjects/(?P<pk>\d+)/$', SubjectDetail.as_view(), name='subject-detail'),
    url(r'^api/visit_types/$', VisitTypeList.as_view(), name='visit-type-list'),
    url(r'^api/visit_types/(?P<pk>\d+)/$', VisitTypeDetail.as_view(), name='visittype-detail'),
)

urlpatterns += patterns('rest_framework',
    url(r'^api-token-auth/', 'authtoken.views.obtain_auth_token'),
)

# Regular web routes
urlpatterns += patterns('repository.views',
    url(r'^403$', 'permission_denied', name='permission_denied'),
    url(r'^$', 'home', name='home'),

    url(r'^antibodies/$', 'view_antibodies', name='view_antibodies'),
    url(r'^antibodies/add/$', 'add_antibody', name='add_antibody'),
    url(r'^antibodies/(?P<antibody_id>\d+)/edit/$', 'edit_antibody', name='edit_antibody'),

    url(r'^fluorochromes/$', 'view_fluorochromes', name='view_fluorochromes'),
    url(r'^fluorochromes/add/$', 'add_fluorochrome', name='add_fluorochrome'),
    url(r'^fluorochromes/(?P<fluorochrome_id>\d+)/edit/$', 'edit_fluorochrome', name='edit_fluorochrome'),

    url(r'^parameters/$', 'view_parameters', name='view_parameters'),
    url(r'^parameters/add/$', 'add_parameter', name='add_parameter'),
    url(r'^parameters/(?P<parameter_id>\d+)/edit/$', 'edit_parameter', name='edit_parameter'),
    url(r'^parameters/(?P<parameter_id>\d+)/select_antibody/$', 'associate_antibody_to_parameter', name='associate_antibody_to_parameter'),
    url(r'^parameters/(?P<parameter_id>\d+)/select_fluorochrome/$', 'associate_fluorochrome_to_parameter', name='associate_fluorochrome_to_parameter'),
    url(r'^parameters/remove_antibody/(?P<pa_map_id>\d+)/$', 'remove_parameter_antibody', name='remove_parameter_antibody'),
    url(r'^parameters/remove_fluorochrome/(?P<pf_map_id>\d+)/$', 'remove_parameter_fluorochrome', name='remove_parameter_fluorochrome'),

    url(r'^specimens/$', 'view_specimens', name='view_specimens'),
    url(r'^specimens/add/$', 'add_specimen', name='add_specimen'),
    url(r'^specimens/(?P<specimen_id>\d+)/edit/$', 'edit_specimen', name='edit_specimen'),

    url(r'^project/(?P<project_id>\d+)$', 'view_project', name='view_project'),
    url(r'^project/add/$', 'add_project', name='add_project'),
    url(r'^project/(?P<project_id>\d+)/edit/$', 'edit_project', name='edit_project'),

    url(r'^project/(?P<project_id>\d+)/users/$', 'view_project_users', name='view_project_users'),
    url(r'^project/(?P<project_id>\d+)/users/add/$', 'add_user_permissions', name='add_user_permissions'),
    url(r'^project/(?P<project_id>\d+)/users/(?P<user_id>-?\d+)/manage/$', 'manage_project_user', name='manage_project_user'),
    url(r'^site/(?P<site_id>\d+)/users/(?P<user_id>-?\d+)/manage/$', 'manage_site_user', name='manage_site_user'),

    url(r'^project/(?P<project_id>\d+)/sites/$', 'view_project_sites', name='view_project_sites'),
    url(r'^project/(?P<project_id>\d+)/sites/add/$', 'add_site', name='add_site'),
    url(r'^site/(?P<site_id>\d+)$', 'view_site', name='view_site'),
    url(r'^site/(?P<site_id>\d+)/edit/$', 'edit_site', name='edit_site'),

    url(r'^site/(?P<site_id>\d+)/uncategorized/$', 'view_site_uncategorized_samples', name='view_site_uncategorized_samples'),
    url(r'^project/(?P<project_id>\d+)/compensations/$', 'view_compensations', name='project_compensations'),
    url(r'^project/(?P<project_id>\d+)/compensations/add/$', 'add_compensation', name='add_compensation'),
    url(r'^site/(?P<site_id>\d+)/compensations/add/$', 'add_site_compensation', name='add_site_compensation'),
    url(r'^download/compensation/(?P<compensation_id>\d+)$', 'retrieve_compensation', name='retrieve_compensation'),

    url(r'^project/(?P<project_id>\d+)/visit_types/$', 'view_visit_types', name='project_visit_types'),
    url(r'^project/(?P<project_id>\d+)/visit_types/add/$', 'add_visit_type', name='add_visit_type'),
    url(r'^project/(?P<project_id>\d+)/visit_types/(?P<visit_type_id>\d+)/edit/$', 'edit_visit_type', name='edit_visit_type'),

    url(r'^project/(?P<project_id>\d+)/panels/$', 'view_project_panels', name='project_panels'),
    url(r'^project/(?P<project_id>\d+)/panels/add/$', 'add_panel', name='add_panel'),
    url(r'^panel/(?P<panel_id>\d+)/edit/$', 'edit_panel', name='edit_panel'),
    url(r'^parameter/(?P<panel_parameter_id>\d+)/remove/$', 'remove_panel_parameter', name='remove_panel_parameter'),

    url(r'^project/(?P<project_id>\d+)/subject_groups/$', 'view_subject_groups', name='subject_groups'),
    url(r'^project/(?P<project_id>\d+)/subject_groups/add/$', 'add_subject_group', name='add_subject_group'),
    url(r'^project/(?P<project_id>\d+)/subject_groups/(?P<subject_group_id>\d+)/edit/$', 'edit_subject_group', name='edit_subject_group'),

    url(r'^project/(?P<project_id>\d+)/subjects/$', 'view_subjects', name='project_subjects'),
    url(r'^subject/(?P<subject_id>\d+)$', 'view_subject', name='view_subject'),
    url(r'^project/(?P<project_id>\d+)/subjects/add/$', 'add_subject', name='add_subject'),
    url(r'^project/(?P<project_id>\d+)/subjects/(?P<subject_id>\d+)/edit/$', 'edit_subject', name='edit_subject'),

    url(r'^sample_groups/$', 'view_sample_groups', name='view_sample_groups'),
    url(r'^sample_groups/add/$', 'add_sample_group', name='add_sample_group'),
    url(r'^sample_groups/(?P<sample_group_id>\d+)/edit/$', 'edit_sample_group', name='edit_sample_group'),

    url(r'^project/(?P<project_id>\d+)/samples/add/$', 'add_sample', name='add_sample'),
    url(r'^subject/(?P<subject_id>\d+)/samples/add/$', 'add_subject_sample', name='add_subject_sample'),
    url(r'^site/(?P<site_id>\d+)/samples/add/$', 'add_site_sample', name='add_site_sample'),

    url(r'^project/(?P<project_id>\d+)/samples/$', 'view_samples', name='project_samples'),
    url(r'^sample/(?P<sample_id>\d+)/edit/$', 'edit_sample', name='edit_sample'),
    url(r'^sample/(?P<sample_id>\d+)/select_panel/$', 'select_panel', name='select_panel'),
    url(r'^sample/(?P<sample_id>\d+)/create_panel/$', 'create_panel_from_sample', name='create_panel_from_sample'),
    url(r'^download/sample/(?P<sample_id>\d+)$', 'retrieve_sample', name='retrieve_sample'),

    url(r'^project/(?P<project_id>\d+)/sample_sets/$', 'view_project_sample_sets', name='view_project_sample_sets'),
    url(r'^project/(?P<project_id>\d+)/sample_sets/add/$', 'add_sample_set', name='add_sample_set'),
    url(r'^sample_set/(?P<sample_set_id>\d+)/$', 'view_sample_set', name='view_sample_set'),

    url(r'^warning$', TemplateView.as_view(template_name='warning.html'), name='warning_page'),
)