# --------  Non-Django imports  ---------
import json
import os
from traceback import format_tb

import redis
import tasktiger
import pickle

# --------  Django imports  -------------
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scheduler.settings')
import django
from django.db import models
from django.conf import settings
from django.utils import timezone

# --------  Project imports  -------------
from scheduler.core.constants import TASK_STATUS, SUBTASK_TYPE
from scheduler.core.crawler.link import Link
from scheduler.core.tasks import runners
# ========================================


def action_handler(subtask, task_config, subtask_config):
    runners.act(task_config, subtask_config)


def crawl_handler(subtask, task_config, subtask_config):
    links = runners.crawl(task_config, subtask_config)

    task = subtask.parent_task
    stage = subtask.stage
    user = subtask_config['user']
    for link, data in links.items():
        binary = pickle.dumps(data)
        task.crawl_links.create(user=user, stage=stage, key=link.page, data=binary)


def analysis_handler(subtask, task_config, subtask_config):
    task = subtask.parent_task
    stage = subtask.stage
    users = task_config['users'].keys()
    links = {}
    for user in users:
        query = task.crawl_links.filter(stage=stage, user=user).values_list('key', 'data')
        links[user] = {Link(key): pickle.loads(data) for (key, data) in query}

    breaches = runners.analyse(task_config, subtask_config, links)

    for link, owner, intruder in breaches:
        task.security_breaches.create(
            stage=stage,
            url=link.page,
            owner=owner,
            intruder=intruder,
        )


SUBTASK_HANDLERS = {
    SUBTASK_TYPE.ACTION: action_handler,
    SUBTASK_TYPE.CRAWL: crawl_handler,
    SUBTASK_TYPE.ANALYSIS: analysis_handler,
}


def subtask_handler(subtask_id):
    django.setup()
    from scheduler.core.models import Subtask
    subtask = Subtask.objects.get(pk=subtask_id)

    task_config = json.loads(subtask.parent_task.configuration)
    subtask_config = json.loads(subtask.configuration)
    handler = SUBTASK_HANDLERS[subtask.type]

    subtask.status = TASK_STATUS.PROCESSING
    subtask.started_at = timezone.now()
    subtask.save(update_fields=('status', 'started_at'))

    try:
        handler(subtask, task_config, subtask_config)
    except Exception as err:
        subtask.status = TASK_STATUS.ERROR
        task = subtask.parent_task
        if task.info is None:
            task.info = ''

        task.info += ' Subtask <stage {}, {}>: "{}", Traceback: "{}";'.format(subtask.stage, subtask.type, err, format_tb(err.__traceback__))
        task.save(update_fields=['info'])
    else:
        subtask.status = TASK_STATUS.DONE

    subtask.finished_at = timezone.now()
    subtask.save(update_fields=('status', 'finished_at'))


class TaskProcessor:
    def __init__(self):
        self.redis_conn = redis.Redis(decode_responses=True)
        self.tiger = tasktiger.TaskTiger(connection=self.redis_conn)

    def run_task(self, subtask):
        tiger_task = tasktiger.Task(
            self.tiger,
            subtask_handler,
            [subtask.pk],
            queue=settings.SCHEDULER_TASKTIGER_QUEUE,
            hard_timeout=settings.SCHEDULER_TASKTIGER_TIMEOUT,
        )
        subtask.tiger_task_id = tiger_task.id
        subtask.save(update_fields=('tiger_task_id',))
        tiger_task.delay()

    def check_user_input(self, task):
        try:
            subtask = task.subtasks.get(stage=task.stage, type=SUBTASK_TYPE.USER_INPUT)
        except models.ObjectDoesNotExist:
            return True  # There can be no subtask of this type
        return subtask.status == TASK_STATUS.DONE

    def check_action(self, task):
        try:
            subtask = task.subtasks.get(stage=task.stage, type=SUBTASK_TYPE.ACTION)
        except models.ObjectDoesNotExist:
            return True  # This is the first stage when we do not apply any actions

        if subtask.status == TASK_STATUS.DONE:
            return True

        if subtask.status == TASK_STATUS.WAITING and subtask.tiger_task_id is None:
            self.run_task(subtask)
        return False

    def check_crawl(self, task):
        subtasks = task.subtasks.filter(stage=task.stage, type=SUBTASK_TYPE.CRAWL).order_by('pk')

        if subtasks.count() == subtasks.filter(status=TASK_STATUS.DONE).count():
            return True

        for subtask in subtasks:
            if subtask.status == TASK_STATUS.WAITING and subtask.tiger_task_id is None:
                self.run_task(subtask)
        return False

    def check_analysis(self, task):
        subtask = task.subtasks.get(stage=task.stage, type=SUBTASK_TYPE.ANALYSIS)

        if subtask.status == TASK_STATUS.DONE:
            return True

        if subtask.status == TASK_STATUS.WAITING and subtask.tiger_task_id is None:
            self.run_task(subtask)
        return False

    def process(self, task):
        # Moving from waiting
        if task.status == TASK_STATUS.WAITING:
            task.status = TASK_STATUS.PROCESSING
            task.stage = 1
            task.save()

        # Updating stage
        current_subtasks = task.subtasks.filter(stage=task.stage)
        if current_subtasks.count() == current_subtasks.filter(status=TASK_STATUS.DONE).count():
            task.stage += 1
            task.save()

        # Marking as done
        if task.stage > task.stages_number:
            task.status = TASK_STATUS.DONE
            task.finished_at = timezone.now()
            task.save()

        # Checking for errors
        if task.subtasks.filter(status=TASK_STATUS.ERROR).exists():
            task.status = TASK_STATUS.ERROR
            task.finished_at = timezone.now()
            task.save()

        # Running subtasks at current stage
        if not self.check_user_input(task):
            return
        if not self.check_action(task):
            return
        if not self.check_crawl(task):
            return
        if not self.check_analysis(task):
            return
