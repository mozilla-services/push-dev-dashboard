# coding: UTF-8
from base64 import urlsafe_b64encode, urlsafe_b64decode
from datetime import datetime
import random
from uuid import UUID

import ecdsa
import fudge
import requests

from django.test import TestCase
from django.utils import timezone

from model_mommy import mommy

from .models import PushApplication, extract_public_key


def _gen_keys():
    signing_key = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p)
    verifying_key = signing_key.get_verifying_key()
    vapid_key = urlsafe_b64encode(verifying_key.to_string())
    return (signing_key, verifying_key, vapid_key)


class PushApplicationTests(TestCase):
    def setUp(self):
        self.user = mommy.make('auth.User')
        self.pa = PushApplication(user=self.user, name='test app')
        self.signing_key, self.verifying_key, self.vapid_key = _gen_keys()
        self.pa.vapid_key = self.vapid_key
        self.pa.save()
        self.tz_aware_now = timezone.make_aware(
            datetime.now(), timezone.get_current_timezone()
        )
        self.fake_post_response_json = {
            'public-key': self.pa.vapid_key,
            'status': 'success'
        }

    def test_default_values(self):
        self.assertEqual(u'pending', self.pa.vapid_key_status)
        self.assertEqual(None, self.pa.validated)
        self.assertIsInstance(self.pa.vapid_key_token, UUID)
        self.assertEqual(4, self.pa.vapid_key_token.version)

    def test_same_app_name_gets_unique_token_value(self):
        pa2 = PushApplication(user=self.user, name=u'test app')
        self.assertNotEqual(self.pa.vapid_key_token, pa2.vapid_key_token)

    @fudge.patch('push.models.PushApplication.start_recording')
    def test_validate_valid_vapid_key_sets_status_starts_recording(
        self, start_recording
    ):
        start_recording.expects_call()
        signature = self.signing_key.sign(str(self.pa.vapid_key_token))
        self.pa.validate_vapid_key(signature)
        self.assertEqual(u'valid', self.pa.vapid_key_status)
        self.assertIsNotNone(self.pa.validated)

    def test_validate_invalid_vapid_key_sets_status(self):
        other_signing_key = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p)
        signature = other_signing_key.sign(str(self.pa.vapid_key_token))
        self.pa.validate_vapid_key(signature)
        self.assertEqual(u'invalid', self.pa.vapid_key_status)

    @fudge.patch('push.models.PushApplication.post_key_to_autopush')
    def test_start_recording_posts_and_sets_status(self,
                                                   post_key_to_autopush):
        post_key_to_autopush.expects_call().returns(
            self.fake_post_response_json
        )
        self.pa.start_recording()
        self.assertEqual('recording', self.pa.vapid_key_status)

    @fudge.patch('push.models.PushApplication.post_key_to_autopush')
    def test_start_recording_handles_connection_error(self,
                                                      post_key_to_autopush):
        pa = mommy.make(PushApplication, vapid_key_status='valid')
        post_key_to_autopush.expects_call().raises(
            requests.ConnectionError("broken")
        )
        pa.start_recording()
        self.assertEqual('valid', pa.vapid_key_status)

    @fudge.patch('requests.post')
    def test_post_key_to_autopush_uses_requests_json(self, post):
        pa = mommy.make(PushApplication, vapid_key_status='valid')
        post.expects_call().returns(
            fudge.Fake().expects('json').returns(
                self.fake_post_response_json
            )
        )
        pa.post_key_to_autopush()


class ExtractPublicKeyTests(TestCase):
    def setUp(self):
        self.spki_header = ('0V0\x10\x06\x04+\x81\x04p\x06\x08*'
                            '\x86H\xce=\x03\x01\x07\x03B\x00\x04')

    def test_extract_public_key_expected(self):
        signing_key, verifying_key, vapid_key = _gen_keys()
        self.assertEqual(urlsafe_b64decode(vapid_key),
                         extract_public_key(urlsafe_b64decode(vapid_key)))

    def test_extract_public_key_raw(self):
        signing_key, verifying_key, vapid_key = _gen_keys()
        vapid_key = urlsafe_b64decode(vapid_key)
        raw_vapid_key = '\x04' + vapid_key
        self.assertEqual(vapid_key,
                         extract_public_key(raw_vapid_key))

    def test_extract_public_key_spki(self):
        signing_key, verifying_key, vapid_key = _gen_keys()
        vapid_key = urlsafe_b64decode(vapid_key)
        spki_vapid_key = self.spki_header + vapid_key
        self.assertEqual(vapid_key,
                         extract_public_key(spki_vapid_key))

    def test_extract_public_key_unknown(self):
        junk64 = ''.join([random.choice('012345abcdef') for i in range(0, 64)])
        self.assertRaises(ValueError, extract_public_key, "banana")
        self.assertRaises(ValueError, extract_public_key, '\x05' + junk64)
        self.assertRaises(ValueError, extract_public_key,
                          junk64[:len(self.spki_header)] + junk64)
        self.assertRaises(ValueError, extract_public_key, junk64[:60])
