from django.db import models

from scheduler.core.constants import TASK_STATUS


class TaskQuerySet(models.QuerySet):
    def unfinished(self):
        return self.filter(
            status__in=(TASK_STATUS.WAITING, TASK_STATUS.PROCESSING),
        )


class TaskManager(models.Manager.from_queryset(TaskQuerySet)):
    pass
