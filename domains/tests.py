from datetime import datetime, timedelta

from uuid import UUID

from django.test import TestCase
from django.utils import timezone

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


class DomainAuthorizationManagerTests(TestCase):
    def setUp(self):
        self.tz_aware_now = timezone.make_aware(
            datetime.now(), timezone.get_current_timezone()
        )
        # A non-expired, valid domain auth
        mommy.make(DomainAuthorization,
                   expires=self.tz_aware_now + timedelta(1),
                   status='valid')
        # An expired, valid domain auth
        mommy.make(DomainAuthorization,
                   expires=self.tz_aware_now - timedelta(1),
                   status='valid')
        # A pending domain auth
        mommy.make(DomainAuthorization,
                   expires=self.tz_aware_now + timedelta(1),
                   status='pending')

    def test_expired(self):
        expired_domain_auths = DomainAuthorization.objects.expired()
        self.assertEquals(1, len(expired_domain_auths))
        for domain_auth in expired_domain_auths:
            self.assertTrue(domain_auth.expires <= self.tz_aware_now)

    def test_need_validation(self):
        domain_auths = DomainAuthorization.objects.need_validation()
        self.assertEquals(2, len(domain_auths))
        for domain_auth in domain_auths:
            self.assertTrue(
                (domain_auth.expires <= self.tz_aware_now) or
                (domain_auth.status == 'pending')
            )
