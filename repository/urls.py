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
    url(r'^api/compensations/$', CompensationList.as_view(), name='compensation-list'),
    url(r'^api/compensations/(?P<pk>\d+)/$', CompensationDetail.as_view(), name='compensation-detail'),
    url(r'^api/panels/$', PanelList.as_view(), name='panel-list'),
    url(r'^api/panels/(?P<pk>\d+)/$', PanelDetail.as_view(), name='panel-detail'),
    url(r'^api/parameters/$', ParameterList.as_view(), name='parameter-list'),
    url(r'^api/parameters/(?P<pk>\d+)/$', ParameterDetail.as_view(), name='parameter-detail'),
    url(r'^api/projects/$', ProjectList.as_view(), name='project-list'),
    url(r'^api/projects/(?P<pk>\d+)/$', ProjectDetail.as_view(), name='project-detail'),
    url(r'^api/samples/$', SampleList.as_view(), name='sample-list'),
    url(r'^api/samples/(?P<pk>\d+)/$', SampleDetail.as_view(), name='sample-detail'),
    url(r'^api/samples/(?P<pk>\d+)/download/$', retrieve_sample, name='sample-download'),
    url(r'^api/samples/(?P<pk>\d+)/apply_panel/$', SamplePanelUpdate.as_view(), name='sample-panel-update'),
    url(r'^api/samples/(?P<pk>\d+)/add_compensation/$', SampleCompensationCreate.as_view(), name='sample-compensation-create'),
    url(r'^api/sites/$', SiteList.as_view(), name='site-list'),
    url(r'^api/sites/(?P<pk>\d+)/$', SiteDetail.as_view(), name='site-detail'),
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
    url(r'^$', 'view_projects', name='home'),
    url(r'^project/(?P<project_id>\d+)$', 'view_project', name='view_project'),
    url(r'^project/add/$', 'add_project', name='add_project'),
    url(r'^project/(?P<project_id>\d+)/edit/$', 'edit_project', name='edit_project'),

    url(r'^project/(?P<project_id>\d+)/sites/$', 'view_sites', name='project_sites'),
    url(r'^project/(?P<project_id>\d+)/sites/add/$', 'add_site', name='add_site'),
    url(r'^site/(?P<site_id>\d+)/edit/$', 'edit_site', name='edit_site'),
    url(r'^project/(?P<project_id>\d+)/compensations/$', 'view_compensations', name='project_compensations'),
    url(r'^site/(?P<site_id>\d+)/compensations/$', 'view_site_compensations', name='site_compensations'),
    url(r'^project/(?P<project_id>\d+)/compensations/add/$', 'add_compensation', name='add_compensation'),
    url(r'^site/(?P<site_id>\d+)/compensations/add/$', 'add_site_compensation', name='add_site_compensation'),
    url(r'^download/compensation/(?P<compensation_id>\d+)$', 'retrieve_compensation', name='retrieve_compensation'),

    url(r'^project/(?P<project_id>\d+)/visit_types/$', 'view_visit_types', name='project_visit_types'),
    url(r'^project/(?P<project_id>\d+)/visit_type/add/$', 'add_visit_type', name='add_visit_type'),
    url(r'^visit_type/(?P<visit_type_id>\d+)/edit/$', 'edit_visit_type', name='edit_visit_type'),

    url(r'^project/(?P<project_id>\d+)/panels/$', 'view_project_panels', name='project_panels'),
    url(r'^project/(?P<project_id>\d+)/panel/add/$', 'add_panel', name='add_panel'),
    url(r'^panel/(?P<panel_id>\d+)/edit/$', 'edit_panel', name='edit_panel'),
    url(r'^parameter/(?P<panel_parameter_id>\d+)/remove/$', 'remove_panel_parameter', name='remove_panel_parameter'),

    url(r'^project/(?P<project_id>\d+)/subjects/$', 'view_subjects', name='project_subjects'),
    url(r'^subject/(?P<subject_id>\d+)$', 'view_subject', name='view_subject'),
    url(r'^project/(?P<project_id>\d+)/subject/add/$', 'add_subject', name='add_subject'),
    url(r'^subject/(?P<subject_id>\d+)/edit/$', 'edit_subject', name='edit_subject'),

    url(r'^project/(?P<project_id>\d+)/sample/add/$', 'add_sample', name='add_sample'),
    url(r'^subject/(?P<subject_id>\d+)/sample/add/$', 'add_subject_sample', name='add_subject_sample'),

    url(r'^project/(?P<project_id>\d+)/samples/$', 'view_samples', name='project_samples'),
    url(r'^sample/(?P<sample_id>\d+)/edit/$', 'edit_sample', name='edit_sample'),
    url(r'^sample/(?P<sample_id>\d+)/select_panel/', 'select_panel', name='select_panel'),
    url(r'^sample/(?P<sample_id>\d+)/create_panel/', 'create_panel_from_sample', name='create_panel_from_sample'),
    url(r'^sample/(?P<sample_id>\d+)/data/', 'sample_data', name='sample_data'),
    url(r'^sample/(?P<sample_id>\d+)/scatterplot/', 'view_sample_scatterplot', name='sample_scatterplot'),
    url(r'^download/sample/(?P<sample_id>\d+)$', 'retrieve_sample', name='retrieve_sample'),

    url(r'^warning$', TemplateView.as_view(template_name='warning.html'), name='warning_page'),
)