# coding: UTF-8
from base64 import urlsafe_b64encode
from datetime import datetime
from uuid import UUID

import ecdsa

from django.test import TestCase
from django.utils import timezone

from model_mommy import mommy

from .models import PushApplication


class PushApplicationTests(TestCase):
    def setUp(self):
        self.user = mommy.make('auth.User')
        self.pa = PushApplication(user=self.user, name='test app')
        self.tz_aware_now = timezone.make_aware(
            datetime.now(), timezone.get_current_timezone()
        )

    def test_default_values(self):
        self.assertEqual(u'pending', self.pa.jws_key_status)
        self.assertEqual(None, self.pa.validated)
        self.assertIsInstance(self.pa.jws_key_token, UUID)
        self.assertEqual(4, self.pa.jws_key_token.version)

    def test_same_app_name_gets_unique_token_value(self):
        pa2 = PushApplication(user=self.user, name=u'test app')
        self.assertNotEqual(self.pa.jws_key_token, pa2.jws_key_token)

    def test_validate_jws_key_valid(self):
        sk256p = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p)
        self.pa.jws_key = urlsafe_b64encode(
            sk256p.get_verifying_key().to_string()
        )
        self.pa.save()

        signature = sk256p.sign(str(self.pa.jws_key_token))
        self.pa.validate_jws_key(signature)
        self.assertEqual(u'valid', self.pa.jws_key_status)
        self.assertIsNotNone(self.pa.validated)

    def test_validate_jws_key_invalid(self):
        sk256p = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p)
        self.pa.jws_key = urlsafe_b64encode(
            sk256p.get_verifying_key().to_string()
        )
        self.pa.save()

        other_sk256p = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p)
        signature = other_sk256p.sign(str(self.pa.jws_key_token))
        self.pa.validate_jws_key(signature)
        self.assertEqual(u'invalid', self.pa.jws_key_status)
