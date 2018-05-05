from django.contrib import admin

from scheduler.core.models import Task, Subtask, CrawlLink, SecurityBreach


admin.site.register(Task)
admin.site.register(Subtask)
admin.site.register(CrawlLink)
admin.site.register(SecurityBreach)
