from django.test import TestCase

from ..apps import ApiConfig


class APIAppTest(TestCase):
    def test_config(self):
        self.assertEqual('api', ApiConfig.name)
