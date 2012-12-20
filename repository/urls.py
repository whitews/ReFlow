from django.conf.urls import patterns, include, url
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
    (r'^project/(?P<project_id>\d+)$', 'view_project'),
    (r'^subject/(?P<subject_id>\d+)$', 'view_subject'),
    (r'^download/sample/(?P<sample_id>\d+)$', 'retrieve_sample'),
    (r'^api/', include(pm_api.urls)),
)