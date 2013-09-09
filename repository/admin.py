from repository.models import *
from django.contrib import admin
from guardian.admin import GuardedModelAdmin

admin.site.register(Antibody)
admin.site.register(Fluorochrome)
admin.site.register(Specimen)


class ProjectAdmin(GuardedModelAdmin):
    user_can_access_owned_objects_only = True
    pass


admin.site.register(Project, ProjectAdmin)


class SiteAdmin(GuardedModelAdmin):
    user_can_access_owned_objects_only = True
    pass


admin.site.register(Site, SiteAdmin)


admin.site.register(SitePanel)
admin.site.register(Parameter)
admin.site.register(ParameterValueType)

admin.site.register(ProjectVisitType)
admin.site.register(SubjectGroup)
admin.site.register(Subject)

admin.site.register(ParameterAntibodyMap)
admin.site.register(ParameterFluorochromeMap)
admin.site.register(SitePanelParameterMap)

admin.site.register(SampleGroup)
admin.site.register(Sample)
admin.site.register(SampleSet)
admin.site.register(SampleParameterMap)
admin.site.register(Compensation)
admin.site.register(SampleCompensationMap)
