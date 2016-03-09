from django.test import TestCase

from ..apps import DomainsConfig


class APIAppTest(TestCase):
    def test_config(self):
        self.assertEqual('domains', DomainsConfig.name)
