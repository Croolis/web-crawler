from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import ElementNotInteractableException

from urllib.parse import urlparse, ParseResult
from tldextract import extract
from bs4 import Tag, BeautifulSoup as bs

from scheduler.core.crawler.action import Action
from scheduler.core.crawler.link import Link
from scheduler.core.crawler.form import Form

from time import sleep

from typing import Set, List, Dict


def get_element(node: bs):
    length = len([sib for sib in node.previous_siblings if isinstance(sib, Tag)]) + 1
    if length > 1:
        return '%s:nth-child(%s)' % (node.name, length)
    else:
        return node.name


def get_xpath(node: bs):
    path = [get_element(node)]
    for parent in node.parents:
        if parent.name == 'body':
            break
        path.insert(0, get_element(parent))
    return 'body > ' + ' > '.join(path)


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
    return len(page_tags & another_page_tags) / len(page_tags | another_page_tags)


def is_new_page(crawled_pages: Dict[Action, str], page_url: str, page_content: str):
    page_url = urlparse(page_url)
    for action in crawled_pages:
        if page_likelihood(page_url, page_content, urlparse(action.page), crawled_pages[action]) > 0.95:
            return False
    return True


def check_url(url: str, domain_url: str) -> bool:
    if url is None or 'javascript:;' in url or '#' in url:
        return False
    url_domain = extract(url)
    expected_domain = extract(domain_url)
    if url_domain.domain != expected_domain.domain or url_domain.suffix != expected_domain.suffix:
        return False
    # search only current domain
    if url_domain.subdomain != expected_domain.subdomain:
        return False
    return True


def login(driver: WebDriver, config: dict, username: str):
    driver.get(config['start_page'])
    for cookie in config['users'][username]:
        driver.add_cookie({'name': cookie, 'value': config['users'][username][cookie]})
    driver.get(config['start_page'])


def logout(driver: WebDriver):
    driver.delete_all_cookies()


def get_actions(driver: WebDriver) -> List[Action]:
    sleep(1)
    links = driver.find_elements_by_tag_name('a')
    actions = set([Link(link.get_attribute('href')) for link in links
                   if check_url(link.get_attribute('href'), driver.current_url)])  # type: Set[Action]
    # actions = set()

    bs_page = bs(driver.page_source)
    for form in bs_page.find_all('form'):
        method = form.get('method') or 'get'  # type: str
        selector = get_xpath(form)
        action = form.get('action') or ''
        status = 'p' if method.lower() == 'get' else 'c'  # type: str
        actions.add(Form(status, driver.current_url, selector, action))
    return sorted(actions)


def perform_action(driver: WebDriver, action: Action):
    try:
        if driver.current_url != action.page:
            driver.get(action.page)
        if isinstance(action, Link):
            pass
        if isinstance(action, Form):
            form = driver.find_element_by_css_selector(action.selector)
            if form is None:
                print("SOMETHING WRONG IS HAPPENING: FORM DISAPPEARED")
            submits = form.find_elements_by_xpath('//input[@type="submit"]') + \
                form.find_elements_by_xpath('//button[@type="submit"]') + \
                form.find_elements_by_xpath('//input[@type="button"]')

            inputs = [inp for inp in form.find_elements_by_xpath('//input')
                      if inp not in submits and inp.get_attribute('type') != 'hidden']
            for visible_input in inputs:
                if visible_input.get_attribute('type') == 'checkbox':
                    visible_input.click()
                else:
                    try:
                        visible_input.send_keys('test')
                    except ElementNotInteractableException:
                        pass
            submits = form.find_elements_by_xpath('//input[@type="submit"]') + \
                form.find_elements_by_xpath('//button[@type="submit"]') + \
                form.find_elements_by_xpath('//input[@type="button"]')
            submits[0].click()
        return True
    except Exception:
        return False


def crawl_page(driver: WebDriver, action: Action,
               performed_actions: Dict[Action, str], blacklisted_actions: Set[Action]):
    print(action)
    print(len(performed_actions))
    print(len(blacklisted_actions))
    if not perform_action(driver, action):
        return
    if not check_url(driver.current_url, action.page):
        # it redirected outside of website
        return
    if not is_new_page(performed_actions, driver.current_url, driver.page_source):
        print('looks like same template')
        blacklisted_actions.add(action)
        return
    performed_actions[action] = driver.page_source
    action.url = driver.current_url

    # collect actions on this page
    actions = get_actions(driver)
    for action in actions:
        if action.status == 'p' and action not in performed_actions and action not in blacklisted_actions:
            crawl_page(driver, action, performed_actions, blacklisted_actions)


def build_site_map(driver: WebDriver, entry_point: str) -> Dict[Action, str]:
    site_map = dict()  # type: Dict[Action, str]
    blacklisted_actions = set()
    crawl_page(driver, Link(entry_point), site_map, blacklisted_actions)
    return site_map


def check_for_escalation(driver: WebDriver, config: dict, site_maps: dict) -> List[tuple]:
    result = []
    for user in site_maps.keys():
        driver.get(config['start_page'])
        logout(driver)
        login(driver, config, user)
        for owner in site_maps.keys():
            if owner == user:
                continue
            for action in site_maps[owner]:
                if action in site_maps[user]:
                    continue
                if perform_action(driver, action) is True and '404' not in driver.page_source\
                        and is_new_page(site_maps[user], driver.current_url, driver.page_source):
                    result.append((action, owner, user))

    return result
