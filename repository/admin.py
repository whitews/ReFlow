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
        qs = Sample.admin  #Use the admin manager regardless of what the default one is

        # we need this from the superclass method
        ordering = self.ordering or ()
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

admin.site.register(Sample, SampleAdmin)


class SampleParameterMapAdmin(admin.ModelAdmin):
    def queryset(self, request):
        qs = SampleParameterMap.admin  #Use the admin manager regardless of what the default one is

        # we need this from the superclass method
        ordering = self.ordering or ()
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

admin.site.register(SampleParameterMap, SampleParameterMapAdmin)
