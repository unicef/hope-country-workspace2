from django.urls import reverse


def check_link_by_class(selenium, cls, view_name):
    link = selenium.find_element_by_class_name(cls)
    url = reverse(f"{view_name}")
    return f' href="{url}"' in link.get_attribute("innerHTML")


def wait_for(driver, *args):
    from selenium.webdriver.support import expected_conditions as ec
    from selenium.webdriver.support.ui import WebDriverWait

    wait = WebDriverWait(driver, 10)
    wait.until(ec.visibility_of_element_located((*args,)))
    return driver.find_element(*args)


def wait_for_url(driver, url):
    from selenium.webdriver.support import expected_conditions as ec
    from selenium.webdriver.support.ui import WebDriverWait

    if "://" not in url:
        url = f"{driver.live_server.url}{url}"
    wait = WebDriverWait(driver, 10)
    wait.until(ec.url_contains(url))


def force_login(user, driver, base_url):
    from importlib import import_module

    from django.conf import settings
    from django.contrib.auth import BACKEND_SESSION_KEY, HASH_SESSION_KEY, SESSION_KEY

    SessionStore = import_module(settings.SESSION_ENGINE).SessionStore  # noqa: N806
    with driver.with_timeouts(page=5):
        driver.get(base_url)

    session = SessionStore()
    session[SESSION_KEY] = user._meta.pk.value_to_string(user)
    session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
    session[HASH_SESSION_KEY] = user.get_session_auth_hash()
    session.save()

    driver.add_cookie(
        {
            "name": settings.SESSION_COOKIE_NAME,
            "value": session.session_key,
            "path": "/",
        }
    )
    driver.refresh()
