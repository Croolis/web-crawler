from django.db import models

from scheduler.core.constants import CRAWL_STATUS


class WorkerHost(models.Model):
    host = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_busy = models.BooleanField(default=False)

    def __repr__(self):
        return '<WorkerHost: {}>'.format(self.host)

    def __str__(self):
        return self.host


class Task(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    configuration = models.TextField()
    name = models.CharField(max_length=64)

    def __repr__(self):
        return '<Task: {}>'.format(self.name)

    def __str__(self):
        return self.name


class CrawlTask(models.Model):
    parent_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='crawl_tasks')
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    random_key = models.CharField(max_length=32)
    worker = models.ForeignKey(WorkerHost, null=True, on_delete=models.SET_NULL, related_name='crawl_tasks')
    status = models.CharField(max_length=16, choices=CRAWL_STATUS.choices())

    def __repr__(self):
        return '<CrawlTask: {}, pk={}>'.format(self.parent_task.name, self.pk)

    def __str__(self):
        return '"{}"-{}'.format(self.parent_task.name, self.pk)
