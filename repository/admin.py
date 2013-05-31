from repository.models import *
from django.contrib import admin

admin.site.register(Antibody)
admin.site.register(Fluorochrome)
admin.site.register(Specimen)

admin.site.register(Project)
admin.site.register(Panel)
admin.site.register(Parameter)
admin.site.register(ParameterValueType)

admin.site.register(ProjectVisitType)
admin.site.register(Site)
admin.site.register(SubjectGroup)
admin.site.register(Subject)

admin.site.register(ParameterAntibodyMap)
admin.site.register(ParameterFluorochromeMap)
admin.site.register(PanelParameterMap)

admin.site.register(SampleGroup)
admin.site.register(Sample)
admin.site.register(SampleParameterMap)
admin.site.register(Compensation)
admin.site.register(SampleCompensationMap)
