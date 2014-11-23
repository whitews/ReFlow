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

admin.site.register(PanelTemplate)
admin.site.register(PanelTemplateParameter)
admin.site.register(PanelTemplateParameterMarker)

admin.site.register(SitePanel)
admin.site.register(SitePanelParameter)
admin.site.register(SitePanelParameterMarker)

admin.site.register(Sample)
admin.site.register(SampleMetadata)
admin.site.register(Compensation)

admin.site.register(SampleCollection)
admin.site.register(SampleCollectionMember)

admin.site.register(Worker)

admin.site.register(SubprocessCategory)
admin.site.register(SubprocessImplementation)
admin.site.register(SubprocessInput)

admin.site.register(ProcessRequest)
admin.site.register(ProcessRequestInput)
admin.site.register(ProcessRequestOutput)
admin.site.register(Cluster)
admin.site.register(SampleCluster)
admin.site.register(SampleClusterParameter)
admin.site.register(EventClassification)