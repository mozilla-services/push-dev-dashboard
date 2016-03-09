from django.test import TestCase

from ..urls import urlpatterns


class APIUrlsTest(TestCase):
    def test_urls(self):
        pattern_names = [p.name for p in urlpatterns[0].url_patterns]
        self.assertIn('api-root', pattern_names)
        self.assertIn('domainauthorization-list', pattern_names)
        self.assertIn('domainauthorization-detail', pattern_names)
        self.assertIn('pushapplication-list', pattern_names)
        self.assertIn('pushapplication-detail', pattern_names)
