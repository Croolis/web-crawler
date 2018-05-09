from selenium.webdriver.remote.webdriver import WebDriver

from urllib.parse import urlparse
from tldextract import extract

from typing import Set, List


def check_url(url: str) -> bool:
    if url is None:
        return False
    url_domain = extract(url)
    expected_domain = extract(ENTRY_POINT)
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


def get_actions(driver: WebDriver) -> List[str]:
    links = driver.find_elements_by_tag_name("a")
    return list(filter(check_url, [link.get_attribute('href') for link in links]))


def crawl_page(driver: WebDriver, url: str, available_links: Set[str]) -> Set[str]:
    driver.get(url)
    available_links.add(url)
    actions = get_actions(driver)
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
