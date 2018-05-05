from django.contrib import admin

from scheduler.core.models import Task, Subtask


admin.site.register(Task)
admin.site.register(Subtask)
