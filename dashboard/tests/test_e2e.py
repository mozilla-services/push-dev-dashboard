import json
import uuid

from decouple import config
from jose import jws
from pywebpush import WebPusher
import py_vapid

from unittest import skipIf

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from django.conf import settings
from django.contrib.staticfiles.testing import LiveServerTestCase

from push.tests import gen_keys

WEBDRIVER_TIMEOUT = config('TESTING_WEBDRIVER_TIMEOUT', 0.0, cast=float)
FXA_ACCOUNT_EMAIL = config('TESTING_FXA_ACCOUNT_EMAIL', None)
FXA_ACCOUNT_PASSWORD = config('TESTING_FXA_ACCOUNT_PASSWORD', None)
PUSH_SERVER_URL = config('TESTING_PUSH_SERVER_URL', None)


@skipIf(WEBDRIVER_TIMEOUT == 0,
        "TESTING_WEBDRIVER_TIMEOUT=0; Skipping SeleniumTests")
@skipIf(settings.DJANGO_DEBUG_TOOLBAR,
        "DJANGO_DEBUG_TOOLBAR=True breaks SeleniumTests; skipping")
@skipIf(FXA_ACCOUNT_EMAIL is None,
        "TESTING_FXA_ACCOUNT_EMAIL is required for SeleniumTests; skipping")
@skipIf(FXA_ACCOUNT_PASSWORD is None,
        "TESTING_FXA_ACCOUNT_PASSWORD is required for SeleniumTests; skipping")
class SeleniumTests(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super(SeleniumTests, cls).setUpClass()
        cls.firefox_profile = FirefoxProfile()
        server_url = config('TEST_PUSH_SERVER_URL', default=False)
        if server_url:
            cls.firefox_profile.set_preference('dom.push.serverURL',
                                               server_url)
        cls.selenium = WebDriver(firefox_profile=cls.firefox_profile)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(SeleniumTests, cls).tearDownClass()

    def setUp(self):
        self.site = config('TESTING_SITE', 'http://127.0.0.1:8000')
        self.email = config('TESTING_FXA_ACCOUNT_EMAIL', None)
        self.password = config('TESTING_FXA_ACCOUNT_PASSWORD', None)
        self.signing_key, self.verifying_key, self.vapid_key = gen_keys()

    def _wait_for_element(self, css_selector):
        wait = WebDriverWait(self.selenium, WEBDRIVER_TIMEOUT)
        wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
        )

    def _wait_for_element_and_click(self, css_selector):
        self._wait_for_element(css_selector)
        self.selenium.find_element_by_css_selector(css_selector).click()

    def test_e2e(self):
        # Go to dashboard and click sign-in
        self.selenium.get('%s' % self.site)
        self._wait_for_element_and_click('a.sign-in-btn')

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
        self._wait_for_element_and_click('a#manage-push-apps-btn')

        # Create a test app with vapid key
        app_name = 'selenium-%s' % str(uuid.uuid4())
        self.selenium.find_element_by_css_selector('input#id_name').send_keys(
            app_name
        )

        self.selenium.find_element_by_css_selector(
            'input#id_vapid_key'
        ).send_keys(
            self.vapid_key
        )

        self.selenium.find_element_by_css_selector("input#add-app-btn").click()

        # Sign JWS claims payload and submit
        jws_claims = self.selenium.find_element_by_css_selector(
            "input#vapid-key-token"
        ).get_attribute('value')

        signed_token = jws.sign(jws_claims,
                                self.signing_key,
                                algorithm='ES256')

        self.selenium.find_element_by_css_selector(
            'input#id_signed_token'
        ).send_keys(
            signed_token
        )

        self.selenium.find_element_by_css_selector(
            "input#validate-jwt-btn"
        ).click()

        self.assertIn(
            'VAPID Key validated',
            self.selenium.find_element_by_css_selector('.callout.success').text
        )

        # go to the push test page to create a pushManager to receive the push
        # test message
        # TODO: use dom.push.testing.ignorePermission in the firefox_profile
        # to make the page skip the permission prompt
        self.selenium.get('%s/push-test-page/' % self.site)

        # get the subscription info object off the page
        self._wait_for_element('pre#subscription_json')
        subscription_json = self.selenium.find_element_by_css_selector(
            'pre#subscription_json'
        )
        subscription = json.loads(subscription_json.text)

        # Send a push message with the VAPID headers
        message = "Testing push service"
        vapid = py_vapid.Vapid(private_key=self.signing_key.to_pem())
        headers = vapid.sign({
            "aud": "http://test.com",
            "sub": "mailto:tester@test.com"
        })
        WebPusher(subscription).send(message, headers)

        # go back to the push app page on the dashboard and poll for the
        # message to show up
        self.selenium.get('%s/push/apps/' % self.site)
        self._wait_for_element_and_click('a#%s' % app_name)

        self._wait_for_element('dl#push-app-info')
        message_found = False
        while not message_found:
            try:
                self.selenium.find_element_by_css_selector('tr.push-message')
                message_found = True
            except NoSuchElementException:
                self.selenium.refresh()
