from django.db import models

from scheduler.core.constants import TASK_STATUS


class Task(models.Model):
    configuration = models.TextField()
    name = models.CharField(max_length=64)
    status = models.CharField(max_length=16, choices=TASK_STATUS.choices(), default=TASK_STATUS.WAITING, blank=True)
    stage = models.IntegerField(default=0, blank=True)
    stages_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    def __repr__(self):
        return '<Task: {}>'.format(self.name)

    def __str__(self):
        return self.name


class CrawlTask(models.Model):
    parent_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='crawl_tasks')
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=TASK_STATUS.choices())

    def __repr__(self):
        return '<CrawlTask: {}, pk={}>'.format(self.parent_task.name, self.pk)

    def __str__(self):
        return '"{}"-{}'.format(self.parent_task.name, self.pk)
