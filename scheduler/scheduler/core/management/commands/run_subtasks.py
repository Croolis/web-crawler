from django.core.management import BaseCommand

from scheduler.core.constants import TASK_STATUS
from scheduler.core.models import Task
from scheduler.core.tasks.crawl_task import TaskProcessor


class Command(BaseCommand):
    def handle(self, *args, **options):
        pending_tasks = Task.objects.filter(status__in=(TASK_STATUS.WAITING, TASK_STATUS.PROCESSING))
        processor = TaskProcessor()

        for task in pending_tasks:
            processor.process(task)
