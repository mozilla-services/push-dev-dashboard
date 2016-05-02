from unittest import skipIf
from decouple import config

from model_mommy import mommy
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import LiveServerTestCase
from django.test import TestCase, override_settings


WEBDRIVER_TIMEOUT = config('TESTING_WEBDRIVER_TIMEOUT', 0.0, cast=float)


# PipelineCachedStorage breaks in some test environments (like Travis)
@override_settings(STATICFILES_STORAGE='pipeline.storage.PipelineStorage')
class UrlTestsFor200(TestCase):
    def setUp(self):
        self.signed_out_urls = ()
        self.signed_in_urls = ()
        self.user = mommy.make(User)
        self.user.set_password('testpass')
        self.user.save()

    def assert_url_200(self, url):
        response = self.client.get(url)
        self.assertEqual(
            200, response.status_code,
            "%s returned %d, not return 200" % (url, response.status_code)
        )

    def assert_all_urls_200(self, urls):
        for url in urls:
            self.assert_url_200(url)

    def test_signed_out_urls(self):
        self.assert_all_urls_200(self.signed_out_urls)

    def test_signed_in_urls(self):
        self.client.login(username=self.user.username, password='testpass')
        self.assert_all_urls_200(self.signed_in_urls)


class DashboardUrlTestsFor200(UrlTestsFor200):
    def setUp(self):
        super(DashboardUrlTestsFor200, self).setUp()
        self.signed_out_urls = (
            '/__heartbeat__',
            '/__lbheartbeat__',
            '/en/',
            '/en/accounts/login/',
        )
        self.signed_in_urls = (
            '/en/',
        )


@skipIf(WEBDRIVER_TIMEOUT == 0, "Skipping SeleniumTests.")
class SeleniumTests(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super(SeleniumTests, cls).setUpClass()
        cls.selenium = WebDriver()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(SeleniumTests, cls).tearDownClass()

    def setUp(self):
        self.site = config('TESTING_SITE', None)
        self.email = config('TESTING_FXA_ACCOUNT_EMAIL', None)
        self.password = config('TESTING_FXA_ACCOUNT_PASSWORD', None)

    def _wait_for_element(self, css_selector):
        wait = WebDriverWait(self.selenium, WEBDRIVER_TIMEOUT)
        wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
        )

    def _wait_for_element_and_click(self, css_selector):
        self._wait_for_element(css_selector)
        self.selenium.find_element_by_css_selector(css_selector).click()

    def test_login(self):
        self.selenium.get('%s' % self.site)
        self.selenium.find_element_by_css_selector("a.sign-in-btn").click()

        # On FxA site, click "Have an account? Sign in." and fill in the form
        self._wait_for_element_and_click('a.sign-in')
        self.selenium.find_element_by_css_selector('input.email').send_keys(
            self.email
        )
        self.selenium.find_element_by_css_selector('input.password').send_keys(
            self.password
        )
        self.selenium.find_element_by_css_selector("button#submit-btn").click()

        # Back at dashboard; should see manage apps button
        self._wait_for_element('a#manage-push-apps-btn')
