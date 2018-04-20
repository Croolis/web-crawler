import redis
import tasktiger

from django.conf import settings
from django.core.management import BaseCommand
from django.db.models import F

from scheduler.core.constants import TASK_STATUS
from scheduler.core.models import Task, CrawlTask
from scheduler.core.tasks.dumb import DumbTaskProcessor


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Marking tasks as DONE
        (
            Task.objects
            .filter(
                status__in=(TASK_STATUS.WAITING, TASK_STATUS.PROCESSING),
                stage__gt=F('stages_number')
            )
            .update(status=TASK_STATUS.DONE)
         )

        unfinished_tasks = (
            Task.objects
            .unfinished()
            .exclude(crawl_tasks__stage=F('stage'))
            .order_by('created_at')
        )

        # Marking waiting tasks as PROCESSING
        unfinished_tasks.filter(stage=0).update(stage=1, status=TASK_STATUS.PROCESSING)

        for task in unfinished_tasks:
            processor = DumbTaskProcessor(task)
            processor.run_subtask()

        # Marking bad crawltasks as ERROR
        conn = redis.Redis(decode_responses=True)
        tiger = tasktiger.TaskTiger(connection=conn)
        running_subtasks = CrawlTask.objects.filter(status=TASK_STATUS.PROCESSING)
        for crawltask in running_subtasks:
            tiger_task = tasktiger.Task.from_id(
                tiger,
                queue=settings.SCHEDULER_TASKTIGER_QUEUE,
                state=tasktiger.ERROR,
                task_id=crawltask.tiger_task_id,
            )
            if tiger_task is not None:
                crawltask.status = TASK_STATUS.ERROR
                crawltask.save(update_fields=['status'])

        # Propagating ERORR status from crawltasks to tasks
        Task.objects.filter(crawl_tasks__status=TASK_STATUS.ERROR).update(status=TASK_STATUS.ERROR)


