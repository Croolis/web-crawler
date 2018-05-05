import time

from scheduler.core.constants import SUBTASK_TYPE


def act(task_config, subtask_config):
    time.sleep(2)


def crawl(task_config, subtask_config):
    time.sleep(120)


def analyse(task_config, subtask_config):
    time.sleep(30)


RUNNERS = {
    SUBTASK_TYPE.ACTION: act,
    SUBTASK_TYPE.CRAWL: crawl,
    SUBTASK_TYPE.ANALYSIS: analyse,
}

