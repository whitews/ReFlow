from repository.models import *
from django.contrib import admin

admin.site.register(Antibody)
admin.site.register(Fluorochrome)

admin.site.register(Project)
admin.site.register(ProjectUserMap)
admin.site.register(Panel)
admin.site.register(Parameter)
admin.site.register(ParameterValueType)

admin.site.register(ProjectVisitType)
admin.site.register(Site)
admin.site.register(Subject)
admin.site.register(Sample)

admin.site.register(ParameterAntibodyMap)
admin.site.register(ParameterFluorochromeMap)
admin.site.register(PanelParameterMap)
admin.site.register(SampleParameterMap)
