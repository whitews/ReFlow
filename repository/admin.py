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

admin.site.register(Stimulation)
admin.site.register(VisitType)
admin.site.register(SubjectGroup)
admin.site.register(Subject)

admin.site.register(ProjectPanel)
admin.site.register(ProjectPanelParameter)
admin.site.register(ProjectPanelParameterAntibody)

admin.site.register(SitePanel)
admin.site.register(SitePanelParameter)
admin.site.register(SitePanelParameterAntibody)

admin.site.register(Sample)
admin.site.register(SampleMetadata)
admin.site.register(SampleSet)
admin.site.register(Compensation)
