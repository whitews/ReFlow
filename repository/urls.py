from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from tastypie.api import Api
from repository.api import *

pm_api = Api(api_name='pm')
pm_api.register(ProjectResource())
pm_api.register(PanelResource())
pm_api.register(ParameterResource())
pm_api.register(SubjectResource())
pm_api.register(SampleResource())
pm_api.register(SampleParameterMapResource())
pm_api.register(AntibodyResource())

urlpatterns = patterns('repository.views',
    url(r'^$', 'projects', name='home'),
    url(r'projects/$', 'projects', name='projects'),
    url(r'^project/(?P<project_id>\d+)$', 'view_project', name='view_project'),
    url(r'^project/add/$', 'add_project', name='add_project'),
    url(r'^project/(?P<project_id>\d+)/sites/$', 'view_project_sites', name='project_sites'),
    url(r'^project/(?P<project_id>\d+)/sites/add/$', 'add_site', name='add_site'),
    url(r'^project/(?P<project_id>\d+)/panels/$', 'view_project_panels', name='project_panels'),
    url(r'^project/(?P<project_id>\d+)/panel/add/$', 'add_panel', name='add_panel'),
    url(r'^subject/(?P<subject_id>\d+)$', 'view_subject'),
    url(r'^download/sample/(?P<sample_id>\d+)$', 'retrieve_sample'),
    url(r'^d3/$', 'd3_test', name='d3_test'),
    url(r'^api/', include(pm_api.urls)),
    url(r'^warning$', TemplateView.as_view(template_name='warning.html'), name='warning_page'),
)