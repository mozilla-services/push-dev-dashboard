from model_mommy import mommy

from django.contrib.auth.models import User
from django.test import TestCase, override_settings


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
