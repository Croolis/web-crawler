from django.contrib import admin

from scheduler.core.models import WorkerHost, Task, CrawlTask


admin.site.register(WorkerHost)
admin.site.register(Task)
admin.site.register(CrawlTask)
