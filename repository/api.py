from django.forms.models import model_to_dict
from tastypie import fields
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS
from repository.models import *

class ProjectResource(ModelResource):
    class Meta:
        queryset = Project.objects.all()
        resource_name = 'project'

class PanelResource(ModelResource):
    project = fields.ToOneField(ProjectResource, 'project')

    class Meta:
        queryset = Panel.objects.all()
        resource_name = 'panel'
        filtering = {
            'project': ALL_WITH_RELATIONS,
        }

class SubjectResource(ModelResource):
    class Meta:
        queryset = Subject.objects.all()
        resource_name = 'subject'
        filtering = {
            'subject_id': ALL_WITH_RELATIONS,
        }

class SampleResource(ModelResource):
    subject = fields.ToOneField(SubjectResource, 'subject')

    parameters = fields.ListField()

    class Meta:
        queryset = Sample.objects.all()
        resource_name = 'sample'
        excludes = ['sample_file']
        filtering = {
            'subject': ALL_WITH_RELATIONS,
        }

    def dehydrate(self, bundle):
        sample_parameter_set = SampleParameterMap.objects.filter(sample=bundle.obj.pk)
        sp_list = []
        for sp in sample_parameter_set:
            sp_dict = {}
            sp_dict['channel_number'] = sp.channel_number
            sp_dict['parameter_short_name'] = sp.parameter.parameter_short_name
            sp_dict['value_type'] = sp.value_type.value_type_short_name
            sp_list.append(sp_dict)
        if sp_list.count > 0:
            bundle.data['parameters'] = sp_list

        return bundle

class ParameterResource(ModelResource):
    sample_set = fields.ToManyField('repository.api.SampleParameterMapResource', 'sampleparametermap_set', full=True)

    class Meta:
        queryset = Parameter.objects.all()
        resource_name = 'parameter'

class SampleParameterMapResource(ModelResource):
    sample = fields.ToOneField(SampleResource, 'sample')
    parameter = fields.ToOneField(ParameterResource, 'parameter')

    class Meta:
        queryset = SampleParameterMap.objects.all()
        resource_name = 'sample_parameter'
        filtering = {
            'sample': ALL_WITH_RELATIONS,
            'parameter': ALL_WITH_RELATIONS,
        }

class AntibodyResource(ModelResource):
    class Meta:
        queryset = Antibody.objects.all()
        resource_name = 'antibody'

class ParameterAntibodyMapResource(ModelResource):
    parameter = fields.ToOneField(ParameterResource, 'parameter')
    antibody = fields.ToOneField(AntibodyResource, 'antibody')

    class Meta:
        queryset = ParameterAntibodyMap.objects.all()
        resource_name = 'parameter_antibody'
