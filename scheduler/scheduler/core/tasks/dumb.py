import json
import os
import redis
import tasktiger
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scheduler.settings')

import django
from django.conf import settings
from django.utils import timezone

from scheduler.core.constants import TASK_STATUS


def do(duration):
    time.sleep(duration)


def subtask(subtask_id):
    django.setup()
    from scheduler.core.models import CrawlTask
    subtask = CrawlTask.objects.get(pk=subtask_id)
    task = subtask.parent_task
    config = json.loads(task.configuration)
    duration = config['tasks'][subtask.stage-1]
    subtask.status = TASK_STATUS.PROCESSING
    subtask.save(update_fields=['status'])

    try:
        do(duration)
    except Exception:
        subtask.status = TASK_STATUS.ERROR
    else:
        subtask.status = TASK_STATUS.DONE
        subtask.finished_at = timezone.now()

    subtask.save()
    task.stage += 1
    task.save(update_fields=['stage'])


class DumbTaskProcessor:
    def __init__(self, task):
        self.task = task
        self.redis_conn = redis.Redis(decode_responses=True)
        self.tiger = tasktiger.TaskTiger(connection=self.redis_conn)

    def run_subtask(self):
        crawltask = self.task.crawl_tasks.create(stage=self.task.stage)

        tiger_task = tasktiger.Task(
            self.tiger,
            subtask,
            [crawltask.pk],
            queue=settings.SCHEDULER_TASKTIGER_QUEUE
        )
        crawltask.tiger_task_id = tiger_task.id
        crawltask.save()

        tiger_task.delay()
