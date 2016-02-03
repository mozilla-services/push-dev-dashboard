from uuid import UUID

from django.test import TestCase

from model_mommy import mommy

from .models import DomainAuthorization


class DomainAuthorizationTests(TestCase):
    def test_default_values(self):
        user = mommy.make('auth.User')
        da = DomainAuthorization(user=user, domain='test.com')
        self.assertEqual('pending', da.status)
        self.assertEqual('dns', da.type)
        self.assertEqual(None, da.validated)
        self.assertEqual(None, da.expires)

    def test_save_generates_valid_uuid5_for_token(self):
        user = mommy.make('auth.User')
        da = DomainAuthorization(user=user, domain='test.com')
        da.save()
        self.assertIsInstance(da.token, UUID)
        self.assertEqual(5, da.token.version)
