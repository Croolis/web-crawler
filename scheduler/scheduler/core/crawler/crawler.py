from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys

from urllib.parse import urlparse, ParseResult
from tldextract import extract
from bs4 import Tag, BeautifulSoup as bs

from scheduler.core.crawler.action import Action
from scheduler.core.crawler.link import Link
from scheduler.core.crawler.form import Form

from time import sleep

from typing import Set, List, Dict


def extract_text(root: bs):
    tags = root.findAll(lambda t: not isinstance(t, Tag) or
                        len([child for child in t.contents if isinstance(child, Tag)]) == 0)
    for tag in tags:
        tag.extract()


def page_likelihood(url: ParseResult, page_content: str, another_url: ParseResult, another_page_content: str):
    page_content = bs(page_content, "html.parser")
    another_page_content = bs(another_page_content, "html.parser")
    path = list(filter(lambda x: len(x), url.path.split("/")))
    another_path = list(filter(lambda x: len(x), another_url.path.split("/")))

    # url likelihood
    if len(path) != len(another_path):
        return 0
    for i in range(len(path) - 2):
        if path[i] != another_path[i]:
            return 0

    # markup likelihood
    extract_text(page_content)
    page_tags = set()
    for tag in page_content.findAll():
        page_tags.add((str(tag.name), frozenset({k: tuple(tag.attrs[k]) for k in tag.attrs})))
    extract_text(another_page_content)
    another_page_tags = set()
    for tag in another_page_content.findAll():
        another_page_tags.add((str(tag.name), frozenset({k: tuple(tag.attrs[k]) for k in tag.attrs})))
    return len(page_tags & another_page_tags) / min(len(page_tags), len(another_page_tags))


def is_new_page(crawled_pages: Dict[Action, str], page_url: str, page_content: str):
    page_url = urlparse(page_url)
    for action in crawled_pages:
        if page_likelihood(page_url, page_content, urlparse(action.url), crawled_pages[action]) > 0.95:
            return False
    return True


def check_url(url: str, domain_url: str) -> bool:
    if url is None:
        return False
    url_domain = extract(url)
    expected_domain = extract(domain_url)
    if url_domain.domain != expected_domain.domain or url_domain.suffix != expected_domain.suffix:
        return False
    if url_domain.subdomain != expected_domain.subdomain:
        return False
    parsed_url = urlparse(url)
    if parsed_url.scheme == 'javascript':
        return False
    return True


def login(driver: WebDriver, config: dict, username: str):
    driver.get(config['start_page'])
    for cookie in config['users'][username]:
        driver.add_cookie({'name': cookie, 'value': config['users'][username][cookie]})


def logout(driver: WebDriver):
    driver.delete_all_cookies()


def get_actions(driver: WebDriver) -> Set[Action]:
    sleep(1)
    links = driver.find_elements_by_tag_name('a')
    actions = set([Link(link.get_attribute('href')) for link in links
                   if check_url(link.get_attribute('href'), driver.current_url)])  # type: Set[Action]

    forms = driver.find_elements_by_tag_name('form')
    current_page = driver.current_url
    for form in forms:
        method = str(form.get_attribute('method')) or 'get'  # type: str
        action = form.get_attribute('action') or 'get'
        status = 'p' if method == 'get' else 'c'  # type: str
        actions.add(Form(status, current_page, action, form.get_attribute('class') or ''))
    return actions


def perform_action(driver: WebDriver, action: Action):
    if driver.current_url != action.page:
        driver.get(action.page)
    if isinstance(action, Link):
        pass
    if isinstance(action, Form):
        submits = driver.find_elements_by_xpath('//form[@class="{}"]//input[@type="submit"]'.format(action.html_class)) +\
                  driver.find_elements_by_xpath('//form[@class="{}"]//button[@type="submit"]'.format(action.html_class)) +\
                  driver.find_elements_by_xpath('//form[@class="{}"]//input[@type="button"]'.format(action.html_class))

        inputs = list(filter(lambda x: x not in submits and x.get_attribute('type') != 'hidden',
                             driver.find_elements_by_xpath('//form[@class="{}"]//input'.format(action.html_class))))
        for visible_input in inputs:
            if visible_input.get_attribute('type') == 'checkbox':
                visible_input.click()
            else:
                visible_input.send_keys('biba')
        if len(submits) > 0:
            submits[0].click()
        else:
            driver.find_elements_by_xpath('//form[@class="{}"]')[0].send_keys(Keys.ENTER)


def crawl_page(driver: WebDriver, action: Action, performed_actions: Dict[Action, str]):
    perform_action(driver, action)
    if not is_new_page(performed_actions, driver.current_url, driver.page_source):
        return
    performed_actions[action] = driver.page_source
    action.url = driver.current_url

    # collect actions on this page
    actions = get_actions(driver)
    for action in actions:
        if action.status == 'p' and action not in performed_actions:
            crawl_page(driver, action, performed_actions)


def build_site_map(driver: WebDriver, entry_point: str) -> Dict[Action, str]:
    site_map = dict()  # type: Dict[Action, str]
    crawl_page(driver, Link(entry_point), site_map)
    return site_map


def check_for_escalation(driver: WebDriver, config: dict, site_maps: dict) -> List[tuple]:
    result = []
    for user in site_maps.keys():
        driver.get(config['start_page'])
        login(driver, config, user)
        for owner in site_maps.keys():
            if owner == user:
                continue
            for link in site_maps[owner]:
                if link in site_maps[user]:
                    continue
                driver.get(link)
                if '404' in driver.page_source:
                    result.append((link, owner, user))

    return result
