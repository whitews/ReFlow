from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from repository.api_views import *

# Override handler403 to provide a custom permission denied page.
# Otherwise, a user has no links to get to their resources
# Esp. useful for 'next' redirection after login
handler403 = TemplateView.as_view(template_name='403.html')

# API routes
urlpatterns = patterns('repository.api_views',
    url(r'^api/$', 'api_root'),
    url(r'^api/projects/$', ProjectList.as_view(), name='project-list'),
    url(r'^api/projects/(?P<pk>\d+)/$', ProjectDetail.as_view(), name='project-detail'),
    url(r'^api/samples/$', SampleList.as_view(), name='sample-list'),
    url(r'^api/samples/(?P<pk>\d+)/$', SampleDetail.as_view(), name='sample-detail'),
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

    url(r'^project/(?P<project_id>\d+)/visit_types/$', 'view_visit_types', name='project_visit_types'),
    url(r'^project/(?P<project_id>\d+)/visit_type/add/$', 'add_visit_type', name='add_visit_type'),

    url(r'^project/(?P<project_id>\d+)/panels/$', 'view_project_panels', name='project_panels'),
    url(r'^project/(?P<project_id>\d+)/panel/add/$', 'add_panel', name='add_panel'),
    url(r'^panel/(?P<panel_id>\d+)/edit/$', 'edit_panel', name='edit_panel'),
    url(r'^parameter/(?P<panel_parameter_id>\d+)/remove/$', 'remove_panel_parameter', name='remove_panel_parameter'),

    url(r'^project/(?P<project_id>\d+)/subjects/$', 'view_subjects', name='project_subjects'),
    url(r'^subject/(?P<subject_id>\d+)$', 'view_subject', name='view_subject'),
    url(r'^project/(?P<project_id>\d+)/subject/add/$', 'add_subject', name='add_subject'),
    url(r'^subject/(?P<subject_id>\d+)/edit/$', 'edit_subject', name='edit_subject'),

    url(r'^subject/(?P<subject_id>\d+)/sample/add/$', 'add_sample', name='add_sample'),

    url(r'^sample/(?P<sample_id>\d+)/select_panel/', 'select_panel', name='select_panel'),
    url(r'^sample/(?P<sample_id>\d+)/data/', 'sample_data', name='sample_data'),
    url(r'^sample/(?P<sample_id>\d+)/scatterplot/', 'view_sample_scatterplot', name='sample_scatterplot'),
    url(r'^download/sample/(?P<sample_id>\d+)$', 'retrieve_sample', name='retrieve_sample'),

    url(r'^warning$', TemplateView.as_view(template_name='warning.html'), name='warning_page'),
)