from tastypie import fields
from tastypie.authentication import BasicAuthentication
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from repository.models import *

class ProjectResource(ModelResource):
    class Meta:
        queryset = Project.objects.all()
        resource_name = 'project'
        filtering = {
            'id': ALL_WITH_RELATIONS,
            'project_name': ALL_WITH_RELATIONS,
        }
        authentication = BasicAuthentication()

class SiteResource(ModelResource):
    project = fields.ToOneField(ProjectResource, 'project')

    class Meta:
        queryset = Site.objects.all()
        resource_name = 'site'
        filtering = {
            'id': ALL_WITH_RELATIONS,
            'project': ALL_WITH_RELATIONS,
        }
        authentication = BasicAuthentication()

class PanelResource(ModelResource):
    project = fields.ToOneField(ProjectResource, 'project')

    class Meta:
        queryset = Panel.objects.all()
        resource_name = 'panel'
        filtering = {
            'project': ALL_WITH_RELATIONS,
        }
        authentication = BasicAuthentication()

class SubjectResource(ModelResource):
    site = fields.ToOneField(SiteResource, 'site')

    class Meta:
        queryset = Subject.objects.all()
        resource_name = 'subject'
        filtering = {
            'subject_id': ALL_WITH_RELATIONS,
            'site': ALL_WITH_RELATIONS,
        }
        authentication = BasicAuthentication()

class SampleResource(ModelResource):
    subject = fields.ToOneField(SubjectResource, 'subject')

    parameters = fields.ToManyField('repository.api.SampleParameterMapResource', 'sampleparametermap_set', full=True)

#    parameters = fields.ListField()

    class Meta:
        queryset = Sample.objects.all()
        resource_name = 'sample'
        excludes = ['sample_file']
        filtering = {
            'subject': ALL_WITH_RELATIONS,
            'parameters': ALL_WITH_RELATIONS,
        }
        authentication = BasicAuthentication()

#    def dehydrate(self, bundle):
#        sample_parameter_set = SampleParameterMap.objects.filter(sample=bundle.obj.pk)
#        sp_list = []
#        for sp in sample_parameter_set:
#            sp_dict = {}
#            sp_dict['parameter_number'] = sp.fcs_number
#            sp_dict['parameter_short_name'] = sp.parameter.parameter_short_name
#            sp_dict['value_type'] = sp.value_type.value_type_short_name
#            sp_list.append(sp_dict)
#        if sp_list.count > 0:
#            bundle.data['parameters'] = sp_list
#
#        return bundle

class ParameterResource(ModelResource):
    samples = fields.ToManyField('repository.api.SampleParameterMapResource', 'sampleparametermap_set', full=True)

    class Meta:
        queryset = Parameter.objects.all()
        resource_name = 'parameter'
        filtering = {
            'samples': ALL_WITH_RELATIONS,
            'fcs_text': ALL,
        }
        authentication = BasicAuthentication()

class SampleParameterMapResource(ModelResource):
    sample = fields.ToOneField(SampleResource, 'sample')
    parameter = fields.ToOneField(ParameterResource, 'parameter')

    class Meta:
        queryset = SampleParameterMap.objects.all()
        resource_name = 'sample_parameter'
        filtering = {
            'sample': ALL_WITH_RELATIONS,
            'parameter': ALL_WITH_RELATIONS,
            'fcs_text': ALL,
        }
        authentication = BasicAuthentication()

class AntibodyResource(ModelResource):
    class Meta:
        queryset = Antibody.objects.all()
        resource_name = 'antibody'
        authentication = BasicAuthentication()

class ParameterAntibodyMapResource(ModelResource):
    parameter = fields.ToOneField(ParameterResource, 'parameter')
    antibody = fields.ToOneField(AntibodyResource, 'antibody')

    class Meta:
        queryset = ParameterAntibodyMap.objects.all()
        resource_name = 'parameter_antibody'
        authentication = BasicAuthentication()
