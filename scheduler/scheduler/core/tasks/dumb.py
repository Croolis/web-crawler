import json
import redis
import tasktiger
import time

from django.conf import settings
from django.utils import timezone

from scheduler.core.constants import TASK_STATUS


def do(duration):
    time.sleep(duration)


def subtask(subtask):
    task = subtask.parent_task
    config = json.loads(task.config)
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
        subtask = self.task.crawl_tasks.create(state=self.task.stage)

        tiger_task = tasktiger.Task(self.tiger, subtask, [subtask], queue=settings.SCHEDULER_TASKTIGER_QUEUE)
        subtask.tiger_task_id = tiger_task.id
        subtask.save()

        tiger_task.delay()
