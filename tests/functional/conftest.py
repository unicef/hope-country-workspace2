import contextlib
import time
from collections import namedtuple
from typing import TYPE_CHECKING

import pytest
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

if TYPE_CHECKING:
    from selenium.webdriver.common.timeouts import Timeouts

Proxy = namedtuple("Proxy", "host,port")


def pytest_configure(config):
    if not config.option.driver:
        config.option.driver = "chrome"


@contextlib.contextmanager
def timeouts(driver, wait=None, page=None, script=None):
    _current: Timeouts = driver.timeouts
    if wait:
        driver.implicitly_wait(wait)
    if page:
        driver.set_page_load_timeout(page)
    if script:
        driver.set_script_timeout(script)
    yield
    driver.timeouts = _current


def set_input_value(driver, *args):
    rules = args[:-1]
    el = driver.find_element(*rules)
    el.clear()
    el.send_keys(args[-1])


def find_by_css(selenium, *args):
    from testutils.selenium import wait_for

    return wait_for(selenium, By.CSS_SELECTOR, *args)


def select2(driver, by, selector, value):
    el = driver.find_element(by, selector)
    el.click()
    time.sleep(1)
    driver.switch_to.active_element.send_keys(value)
    driver.find_element(By.XPATH, f"//div[contains(text(),'{value}')]").click()
    time.sleep(1)
    driver.switch_to.active_element.send_keys(Keys.TAB)
    time.sleep(1)
    driver.switch_to.active_element.send_keys(Keys.TAB)


@pytest.fixture
def chrome_options(request, chrome_options):
    if not request.config.getvalue("show_browser"):
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--allow-insecure-localhost")
    chrome_options.add_argument("--disable-browser-side-navigation")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-translate")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--lang=en-GB")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--proxy-bypass-list=*")
    chrome_options.add_argument("--proxy-server='direct://'")
    chrome_options.add_argument("--start-maximized")

    prefs = {"profile.default_content_setting_values.notifications": 1}  # explicitly allow notifications
    chrome_options.add_experimental_option("prefs", prefs)

    return chrome_options


SELENIUM_DEFAULT_PAGE_LOAD_TIMEOUT = 5
SELENIUM_DEFAULT_IMPLICITLY_WAIT = 1
SELENIUM_DEFAULT_SCRIPT_TIMEOUT = 1


@pytest.fixture
def selenium(monkeypatch, live_server, settings, driver):
    from testutils.selenium import wait_for, wait_for_url

    settings.FLAGS = {"LOCAL_LOGIN": [("boolean", True)]}

    driver.with_timeouts = timeouts.__get__(driver)
    driver.set_input_value = set_input_value.__get__(driver)
    driver.live_server = live_server
    driver.wait_for = wait_for.__get__(driver)
    driver.wait_for_url = wait_for_url.__get__(driver)
    driver.find_by_css = find_by_css.__get__(driver)
    driver.select2 = select2.__get__(driver)

    return driver
