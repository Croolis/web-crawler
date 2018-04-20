from django.contrib import admin

from scheduler.core.models import Task, CrawlTask


admin.site.register(Task)
admin.site.register(CrawlTask)
