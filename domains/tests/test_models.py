from datetime import datetime, timedelta
from uuid import UUID

import fudge

from django.test import TestCase
from django.utils import timezone

from model_mommy import mommy

from ..models import DomainAuthorization


class DomainAuthorizationTests(TestCase):
    def setUp(self):
        self.user = mommy.make('auth.User')
        self.da = DomainAuthorization(
            user=self.user,
            domain='test.com',
            type='dns'
        )
        self.tz_aware_now = timezone.make_aware(
            datetime.now(), timezone.get_current_timezone()
        )

    def test_default_values(self):
        self.assertEqual('pending', self.da.status)
        self.assertEqual('dns', self.da.type)
        self.assertEqual(None, self.da.validated)
        self.assertEqual(None, self.da.expires)

    def test_save_generates_valid_uuid4_for_token(self):
        self.da.save()
        self.assertIsInstance(self.da.token, UUID)
        self.assertEqual(4, self.da.token.version)

    def test_same_domain_gets_unique_token_value(self):
        da2 = DomainAuthorization(user=self.user, domain='test.com')
        self.assertNotEqual(self.da.token, da2.token)

    # patch out the model DNS method
    @fudge.patch('domains.models.DomainAuthorization.get_dns_txt_record')
    def test_validate_dns_type(self, get_dns_txt_record):
        fake_record = fudge.Fake().has_attr(
            a=fudge.Fake().has_attr(
                rdata='"%s"' % self.da.token
            )
        )
        get_dns_txt_record.expects_call().returns(fake_record)
        self.da.validate()
        self.assertEqual('valid', self.da.status)
        self.assertIsNotNone(self.da.validated)
        self.assertTrue(self.da.expires > self.tz_aware_now)


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
