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

admin.site.register(ParameterAntibodyMap)
admin.site.register(ParameterFluorochromeMap)
admin.site.register(PanelParameterMap)


class SampleAdmin(admin.ModelAdmin):
    def queryset(self, request):
        return super(SampleAdmin, self).queryset(request).defer("array_data", )

admin.site.register(Sample, SampleAdmin)


class SampleParameterMapAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super(SampleParameterMapAdminManager, self).queryset(request).defer("sample__array_data",)

admin.site.register(SampleParameterMap, SampleParameterMapAdmin)
