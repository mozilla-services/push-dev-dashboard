# coding: UTF-8
from base64 import urlsafe_b64decode
import json
import random
from uuid import UUID

import ecdsa
import fudge
from fudge.inspector import arg
from jose import jws
import requests

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User

from model_mommy import mommy

from ..models import PushApplication, MessagesAPIError
from ..models import (extract_public_key, fix_padding, get_autopush_endpoint,
                      delete_key_from_messages_api)
from .. import NO_MESSAGES
from . import (MESSAGES_API_RESPONSE_JSON_MESSAGES, MESSAGES_API_POST_RESPONSE,
               gen_keys)


class PushApplicationTestCase(TestCase):
    def setUp(self):
        self.user = mommy.make('auth.User')
        self.pa = PushApplication(user=self.user, name='test app')
        self.signing_key, self.verifying_key, self.vapid_key = gen_keys()
        self.pa.vapid_key = self.vapid_key
        self.pa.save()
        self.tz_aware_now = timezone.now()
        self.fake_get_response_json = {
            'public-key': self.pa.vapid_key,
            'messages': MESSAGES_API_RESPONSE_JSON_MESSAGES
        }


class PushApplicationTests(PushApplicationTestCase):
    def test_default_values(self):
        self.assertEqual(u'pending', self.pa.vapid_key_status)
        self.assertEqual(None, self.pa.validated)

    def test_vapid_key_token_is_aud_claim(self):
        token_json = json.loads(self.pa.vapid_key_token)
        self.assertTrue("http" in token_json['aud'])
        aud_uuid = token_json['aud'].split('/')[-1]
        self.assertIsInstance(UUID(aud_uuid), UUID)

    def test_same_app_name_gets_unique_token_value(self):
        pa2 = PushApplication(user=self.user, name=u'test app')
        self.assertNotEqual(self.pa.vapid_key_token, pa2.vapid_key_token)

    def test_status_shortcut_methods(self):
        pending_app = PushApplication()
        valid_app = PushApplication(vapid_key_status='valid')
        invalid_app = PushApplication(vapid_key_status='invalid')
        recording_app = PushApplication(vapid_key_status='recording')

        self.assertTrue(pending_app.can_validate())
        self.assertTrue(invalid_app.can_validate())
        self.assertFalse(valid_app.can_validate())
        self.assertFalse(recording_app.can_validate())

        self.assertTrue(valid_app.valid())
        self.assertTrue(recording_app.valid())
        self.assertFalse(invalid_app.valid())
        self.assertFalse(pending_app.valid())

        self.assertTrue(invalid_app.invalid())
        self.assertFalse(valid_app.invalid())

        self.assertTrue(recording_app.recording())
        self.assertFalse(pending_app.recording())

    @fudge.patch('push.models.PushApplication.start_recording')
    def test_validate_valid_vapid_key_sets_status_starts_recording(
        self, start_recording
    ):
        start_recording.expects_call()
        signed_token = jws.sign(self.pa.vapid_key_token,
                                self.signing_key,
                                algorithm='ES256')
        self.pa.validate_vapid_key(signed_token)
        self.assertEqual(u'valid', self.pa.vapid_key_status)
        self.assertIsNotNone(self.pa.validated)

    @fudge.patch('push.models.PushApplication.start_recording')
    def test_validate_invalid_vapid_key_sets_status(self, start_recording):
        start_recording.is_callable().times_called(0)

        other_signing_key = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p)
        signed_token = jws.sign(self.pa.vapid_key_token,
                                other_signing_key,
                                algorithm='ES256')
        self.pa.validate_vapid_key(signed_token)
        self.assertEqual(u'invalid', self.pa.vapid_key_status)

    @fudge.patch('requests.get')
    def test_created_by_returns_true_for_match(self, get):
        openjck = User.objects.create_user('openjck',
                                           'example@example.com',
                                           'password')
        pa = mommy.make(PushApplication, user=openjck)
        self.assertTrue(pa.created_by(openjck))

    @fudge.patch('requests.get')
    def test_created_by_returns_false_for_mismatch(self, get):
        openjck = User.objects.create_user('openjck',
                                           'example@example.com',
                                           'password')
        some_other_user = User.objects.create_user('SomeOtherUser',
                                                   'example@example.com',
                                                   'password')
        pa = mommy.make(PushApplication, user=openjck)
        self.assertFalse(pa.created_by(some_other_user))


class PushApplicationMessagesAPITests(PushApplicationTestCase):
    @fudge.patch('push.models.PushApplication.post_key_to_api')
    def test_start_recording_calls_api_and_sets_status(self, post_key_to_api):
        self.pa.vapid_key_status = 'valid'
        post_key_to_api.expects_call().returns(MESSAGES_API_POST_RESPONSE)

        self.pa.start_recording()
        self.assertEqual('recording', self.pa.vapid_key_status)

    @fudge.patch('requests.request')
    def test_post_key_to_api_uses_requests_json(self, request):
        pa = mommy.make(PushApplication, vapid_key_status='valid')
        request.expects_call().with_args(
            'post',
            arg.any(),
            json={'public-key': pa.vapid_key},
            timeout=arg.any()
        ).returns(
            MESSAGES_API_POST_RESPONSE
        )
        pa.post_key_to_api()

    @fudge.patch('requests.request')
    def test_post_key_to_api_MessagesAPIError_on_connection_error(self,
                                                                  request):
        pa = mommy.make(PushApplication, vapid_key_status='valid')
        request.expects_call().raises(
            requests.ConnectionError("broken")
        )
        with self.assertRaises(MessagesAPIError):
            pa.post_key_to_api()
        self.assertEqual('valid', pa.vapid_key_status)

    @fudge.patch('requests.request')
    def test_post_key_to_api_MessagesAPIError_on_status_500(self,
                                                            request):
        request.expects_call().returns(
            fudge.Fake().has_attr(status_code=500, content='Status: 500')
        )
        pa = mommy.make(PushApplication, vapid_key_status='valid')
        with self.assertRaisesRegexp(MessagesAPIError, 'Status: 500'):
            pa.post_key_to_api()
        self.assertEqual('valid', pa.vapid_key_status)

    @fudge.patch('requests.request')
    def test_get_messages_not_recording_returns_empty(self, request):
        pa = mommy.make(PushApplication, vapid_key_status='valid')
        request.is_callable().times_called(0)

        self.assertEqual(NO_MESSAGES, pa.get_messages())

    @fudge.patch('requests.request')
    def test_get_messages_uses_requests_json(self, request):
        pa = mommy.make(PushApplication, vapid_key_status='recording')
        request.expects_call().returns(
            fudge.Fake().has_attr(status_code=200).expects('json').returns(
                self.fake_get_response_json
            )
        )
        pa.get_messages()

    @fudge.patch('requests.request')
    def test_get_messages_204_returns_empty_messages(self, request):
        pa = mommy.make(PushApplication, vapid_key_status='recording')
        request.expects_call().returns(fudge.Fake().has_attr(status_code=204))

        self.assertEqual(NO_MESSAGES, pa.get_messages())

    @fudge.patch('requests.request')
    def test_get_messages_MessagesAPIError_on_connection_error(self, request):
        pa = mommy.make(PushApplication, vapid_key_status='recording')
        request.expects_call().raises(
            requests.ConnectionError("broken")
        )
        with self.assertRaises(MessagesAPIError):
            pa.get_messages()

    @fudge.patch('requests.request')
    def test_get_messages_MessagesAPIError_404_reverts_status(self, request):
        pa = mommy.make(PushApplication, vapid_key_status='recording')
        pa2 = mommy.make(PushApplication, vapid_key_status='recording')
        request.expects_call().returns(
            fudge.Fake().has_attr(status_code=404)
        )
        with self.assertRaises(MessagesAPIError):
            pa.get_messages()
        pa = PushApplication.objects.get(pk=pa.id)
        pa2 = PushApplication.objects.get(pk=pa2.id)
        self.assertEqual('valid', pa.vapid_key_status)
        self.assertEqual('valid', pa2.vapid_key_status)

    @fudge.patch('requests.request')
    def test_delete_key_from_messages_api_204(self, request):
        pa = mommy.make(PushApplication, vapid_key_status='recording')
        request.expects_call().with_args(
            'delete',
            arg.any(),
            json=arg.any(),
            timeout=arg.any()
        ).returns(
            fudge.Fake().has_attr(status_code=204)
        )

        delete_key_from_messages_api(PushApplication, pa)

    @fudge.patch('requests.request')
    def test_delete_key_from_messages_api_404(self, request):
        # TODO: Decide what to do with 404 responses to DELETE
        # https://github.com/mozilla-services/push-dev-dashboard/issues/205#issuecomment-217182142
        pa = mommy.make(PushApplication, vapid_key_status='recording')
        request.expects_call().with_args(
            'delete',
            arg.any(),
            json=arg.any(),
            timeout=arg.any()
        ).returns(
            fudge.Fake().has_attr(status_code=404)
        )

        with self.assertRaises(MessagesAPIError):
            delete_key_from_messages_api(PushApplication, pa)


class GetAutopushEndpointTests(TestCase):
    def test_missing_value_raises_exception(self):
        prev_value = settings.PUSH_MESSAGES_API_ENDPOINT
        settings.PUSH_MESSAGES_API_ENDPOINT = None
        with self.assertRaises(ImproperlyConfigured):
            get_autopush_endpoint()
        settings.PUSH_MESSAGES_API_ENDPOINT = prev_value


class FixPaddingTests(TestCase):
    def setUp(self):
        self.unpadded = ('BKN35wUomETjgRqu93qQiAt58NV3aeBX6dx4WIJVZpr2MqF4JQ8v'
                         'GThfzmFsN15gJx2vldoUCjWuVXkTohV1klE')
        self.padded = ('BKN35wUomETjgRqu93qQiAt58NV3aeBX6dx4WIJVZpr2MqF4JQ8v'
                       'GThfzmFsN15gJx2vldoUCjWuVXkTohV1klE=')

    def test_unpadded_becomes_multiple_of_4(self):
        self.assertEqual(0, len(fix_padding(self.unpadded)) % 4)
        self.assertEqual(0, len(fix_padding(self.padded)) % 4)


class ExtractPublicKeyTests(TestCase):
    def setUp(self):
        self.spki_header = ('0V0\x10\x06\x04+\x81\x04p\x06\x08*'
                            '\x86H\xce=\x03\x01\x07\x03B\x00\x04')

    def test_extract_public_key_expected(self):
        signing_key, verifying_key, vapid_key = gen_keys()
        self.assertEqual(urlsafe_b64decode(vapid_key),
                         extract_public_key(urlsafe_b64decode(vapid_key)))

    def test_extract_public_key_raw(self):
        signing_key, verifying_key, vapid_key = gen_keys()
        vapid_key = urlsafe_b64decode(vapid_key)
        raw_vapid_key = '\x04' + vapid_key
        self.assertEqual(vapid_key,
                         extract_public_key(raw_vapid_key))

    def test_extract_public_key_spki(self):
        signing_key, verifying_key, vapid_key = gen_keys()
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
