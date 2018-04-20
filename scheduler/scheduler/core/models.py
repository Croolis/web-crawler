from django.db import models
from django.utils import timezone

from scheduler.core.constants import TASK_STATUS
from scheduler.core.managers import TaskManager


def elapsed_time(object):
    finish_time = object.finished_at if object.finished_at else timezone.now()
    seconds = (finish_time - object.created_at).total_seconds()
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    values = [
        '{}h'.format(hours) if hours else '',
        '{}m'.format(mins) if mins else '',
        '{}s'.format(secs) if secs else ''
    ]
    return ' '.join('{:>3}'.format(val) for val in values)


class Task(models.Model):
    configuration = models.TextField()
    name = models.CharField(max_length=64)
    status = models.CharField(max_length=16, choices=TASK_STATUS.choices(), default=TASK_STATUS.WAITING, blank=True)
    stage = models.IntegerField(default=0, blank=True)
    stages_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    objects = TaskManager()

    @property
    def sorted_crawltasks(self):
        return self.crawl_tasks.order_by('stage')

    @property
    def running(self):
        return elapsed_time(self)

    def __repr__(self):
        return '<Task: {}>'.format(self.name)

    def __str__(self):
        return self.name


class CrawlTask(models.Model):
    parent_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='crawl_tasks')
    stage = models.IntegerField()
    status = models.CharField(max_length=16, choices=TASK_STATUS.choices(), default=TASK_STATUS.WAITING)
    tiger_task_id = models.CharField(null=True, max_length=64)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    @property
    def running(self):
        return elapsed_time(self)

    def __repr__(self):
        return '<CrawlTask: {}, pk={}>'.format(self.parent_task.name, self.pk)

    def __str__(self):
        return '"{}"-{}'.format(self.parent_task.name, self.pk)
