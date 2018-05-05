from django.db import models
from django.utils import timezone
import json

from scheduler.core.constants import TASK_STATUS, SUBTASK_TYPE
from scheduler.core.managers import TaskManager


def elapsed_time(obj, start_time_attr):
    start_time = getattr(obj, start_time_attr)
    if not start_time:
        return '–'
    finish_time = obj.finished_at if obj.finished_at else timezone.now()
    seconds = (finish_time - start_time).total_seconds()
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
    info = models.TextField(null=True, blank=True)

    objects = TaskManager()

    @property
    def sorted_subtasks(self):
        subtasks = []
        for stage in range(1, self.stages_number+1):
            subtasks.append(self.subtasks.filter(stage=stage).order_by('pk'))
        return subtasks

    @property
    def running(self):
        return elapsed_time(self, 'created_at')

    def __repr__(self):
        return '<Task: {}>'.format(self.name)

    def __str__(self):
        return self.name


class Subtask(models.Model):
    parent_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    stage = models.IntegerField()
    type = models.CharField(max_length=16, choices=SUBTASK_TYPE.choices())
    configuration = models.TextField(null=True)
    status = models.CharField(max_length=16, choices=TASK_STATUS.choices(), default=TASK_STATUS.WAITING)
    tiger_task_id = models.CharField(null=True, max_length=64)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    @property
    def running(self):
        return elapsed_time(self, 'started_at')

    @property
    def task_user(self):
        if self.type == SUBTASK_TYPE.ACTION:
            return json.loads(self.configuration).get('action')
        elif self.type == SUBTASK_TYPE.CRAWL:
            return json.loads(self.configuration).get('user')
        else:
            return ''

    def __repr__(self):
        return '<Subtask: {}, pk={}>'.format(self.parent_task.name, self.pk)

    def __str__(self):
        return '"{}"-{}'.format(self.parent_task.name, self.pk)


class CrawlLink(models.Model):
    url = models.URLField()
    task = models.ForeignKey(Task, related_name='crawl_links', on_delete=models.CASCADE)
    stage = models.IntegerField()
    user = models.CharField(max_length=32)

    def __str__(self):
        return '<Link: task="{}"-{}, user={}, url={}>'.format(
            self.task.name,
            self.stage,
            self.user,
            self.url,
        )

    class Meta:
        indexes = [
            models.Index(fields=['task', 'stage', 'user']),
        ]


class SecurityBreach(models.Model):
    url = models.URLField()
    task = models.ForeignKey(Task, related_name='security_breaches', on_delete=models.CASCADE)
    stage = models.IntegerField()
    owner = models.CharField(max_length=32)
    intruder = models.CharField(max_length=32)

    def __str__(self):
        return '<Breach: task="{}"-{}, owner={}, intruder={}, url={}>'.format(
            self.task.name,
            self.stage,
            self.owner,
            self.intruder,
            self.url,
        )

    class Meta:
        indexes = [
            models.Index(fields=['task', 'stage']),
        ]
        ordering = ['stage', 'owner', 'intruder']
