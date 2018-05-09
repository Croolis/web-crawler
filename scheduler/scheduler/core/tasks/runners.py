import time

from scheduler.scheduler.core.crawler.crawler import build_site_map, check_for_escalation, login, logout
from selenium import webdriver

firefox_driver = webdriver.Firefox()


def act(task_config, subtask_config):
    time.sleep(1)
    return None


def crawl(task_config, subtask_config):
    user = subtask_config['user']
    login(firefox_driver, task_config, user)
    entry_point = task_config['start_page']
    site_map = build_site_map(firefox_driver, entry_point)
    logout(firefox_driver)
    return site_map


def analyse(task_config, subtask_config, site_maps):
    escalations = check_for_escalation(firefox_driver, task_config, site_maps)
    return escalations
