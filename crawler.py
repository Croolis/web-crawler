from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

from urllib.parse import urlparse
from tldextract import extract

from typing import Set, List

ENTRY_POINT = "https://www.jetbrains.com"


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
    for action in actions:
        if action in available_links:
            continue
        crawl_page(driver, action, available_links)

    return available_links


def build_site_maps(driver: WebDriver, entry_point: str):
    site_maps = dict()
    role = 'guest'
    while role != 'no':
        site_map = build_site_map(driver, entry_point)
        site_maps[role] = site_map
        driver.get(entry_point)
        role = input("Please login and type user role to continue parsing as another user. Type 'no' to finish preparation phase and check for vulnerabilities.")
    return site_maps


def build_site_map(driver: WebDriver, entry_point: str):
    site_map = set()
    crawl_page(driver, entry_point, all_links)
    driver.delete_all_cookies()
    return site_map


def check_for_escalation(driver: WebDriver, site_maps):
    for role in site_maps.keys():
        driver.get(entry_point)
        input('Please login as {} and press ENTER'.format(role))
        for other_role in site_maps.keys():
            if other_role == role:
                continue
            for link in site_maps[other_role]:
                if link not in site_maps[role]:
                    driver.get(link)
                    if '404' in driver.page_source:
                        print('User {} can access {} via direct link, but cannot access this page via interface'.format(role, link))
 


firefox_driver = webdriver.Firefox()
site_maps = build_site_maps(firefox_driver, ENTRY_POINT)
check_for_escalation(firefox_driver, site_maps)
firefox_driver.close()
print(all_links)
