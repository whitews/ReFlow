from process_manager.models import *
from django.contrib import admin

admin.site.register(Process)
admin.site.register(ProcessInput)

admin.site.register(Worker)

admin.site.register(ProcessRequest)
admin.site.register(ProcessRequestInputValue)