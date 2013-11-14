from repository.models import *
from django.contrib import admin
from guardian.admin import GuardedModelAdmin

admin.site.register(Marker)
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
admin.site.register(ProjectPanelParameterMarker)

admin.site.register(SitePanel)
admin.site.register(SitePanelParameter)
admin.site.register(SitePanelParameterMarker)

admin.site.register(Sample)
admin.site.register(SampleMetadata)
admin.site.register(Compensation)

admin.site.register(Process)
admin.site.register(ProcessInput)

admin.site.register(Worker)

admin.site.register(ProcessRequest)
admin.site.register(ProcessRequestInputValue)