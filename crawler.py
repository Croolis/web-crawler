from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

from urllib.parse import urlparse
from tldextract import extract

from typing import Set, List

ENTRY_POINT = "http://www.python.org"


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


def get_actions(driver: WebDriver) -> List[str]:
    links = driver.find_elements_by_tag_name("a")
    return list(filter(check_url, [link.get_attribute('href') for link in links]))


def crawl_page(driver: WebDriver, url: str, available_links: Set[str]) -> Set[str]:
    driver.get(url)
    available_links.add(url)
    actions = get_actions(driver)
    print(actions)
    for action in actions:
        if action in available_links:
            continue
        crawl_page(driver, action, available_links)

    return available_links


firefox_driver = webdriver.Firefox()
all_links = set()
crawl_page(firefox_driver, ENTRY_POINT, all_links)
firefox_driver.close()
print(all_links)
