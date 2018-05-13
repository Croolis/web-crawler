from selenium.webdriver.remote.webdriver import WebDriver

from urllib.parse import urlparse, ParseResult
from tldextract import extract

from typing import Set, List, Dict

from bs4 import Tag, BeautifulSoup as bs


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


def is_new_page(crawled_pages: Dict[str, str], page_url: str, page_content: str):
    page_url = urlparse(page_url)
    for crawled_url in crawled_pages:
        if page_likelihood(page_url, page_content, urlparse(crawled_url), crawled_pages[crawled_url]) > 0.95:
            return False
    return True


def check_url(url: str, domain_url: str) -> bool:
    if url is None:
        return False
    url_domain = extract(url)
    expected_domain = extract(domain_url)
    if url_domain.domain != expected_domain.domain or url_domain.suffix != expected_domain.suffix:
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


def get_actions(driver: WebDriver, url: str) -> List[str]:
    links = driver.find_elements_by_tag_name("a")
    return [link.get_attribute('href') for link in links if check_url(link.get_attribute('href'), driver.current_url)]


def crawl_page(driver: WebDriver, url: str, available_links: Set[str]) -> Set[str]:
    driver.get(url)
    available_links.add(url)
    actions = get_actions(driver, url)
    for action in actions:
        if action in available_links:
            continue
        crawl_page(driver, action, available_links)

    return available_links


def build_site_map(driver: WebDriver, entry_point: str):
    site_map = set()
    crawl_page(driver, entry_point, site_map)

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
