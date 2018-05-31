from scheduler.core.crawler.crawler import build_site_map, check_for_escalation, login, logout
from selenium import webdriver


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('no-sandbox')
    options.add_argument('window-size=1200x600')
    return webdriver.Chrome(chrome_options=options)


def act(task_config, subtask_config):
    driver = get_driver()
    action_name = subtask_config['action']
    form_data = subtask_config['form_data']
    action_config = task_config['actions'][action_name]
    user = action_config['user']
    login(driver, task_config, user)
    driver.get(action_config['page'])
    if action_config['type'] == 'link':
        pass
    if action_config['type'] == 'form':
        # fill form
        for input_selector in form_data:
            inp = driver.find_element_by_css_selector(input_selector)
            inp.send_keys(form_data[input_selector])
        # submit form
        driver.find_element_by_css_selector(action_config['submit']).click()
    if action_config['type'] == 'clickable':
        # click on clickable object
        driver.find_element_by_css_selector(action_config['submit']).clickable.click()
    driver.quit()
    return None


def crawl(task_config, subtask_config):
    driver = get_driver()
    user = subtask_config['user']
    login(driver, task_config, user)
    entry_point = task_config['start_page']
    site_map = build_site_map(driver, entry_point)
    logout(driver)
    driver.quit()
    return site_map


def analyse(task_config, subtask_config, site_maps):
    driver = get_driver()
    escalations = check_for_escalation(driver, task_config, site_maps)
    driver.quit()
    return escalations
