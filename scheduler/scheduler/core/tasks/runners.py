import time

from scheduler.core.crawler.crawler import build_site_map, check_for_escalation, login, logout
from selenium import webdriver


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('no-sandbox')
    options.add_argument('window-size=1200x600')
    return webdriver.Chrome(chrome_options=options)


def act(task_config, subtask_config):
    time.sleep(1)
    return None


def crawl(task_config, subtask_config):
    firefox_driver = get_driver()
    user = subtask_config['user']
    login(firefox_driver, task_config, user)
    entry_point = task_config['start_page']
    site_map = build_site_map(firefox_driver, entry_point)
    logout(firefox_driver)
    firefox_driver.quit()
    return site_map


def analyse(task_config, subtask_config, site_maps):
    firefox_driver = get_driver()
    escalations = check_for_escalation(firefox_driver, task_config, site_maps)
    firefox_driver.quit()
    return escalations
