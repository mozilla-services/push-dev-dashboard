from __future__ import unicode_literals
from base64 import urlsafe_b64decode
from datetime import datetime
import uuid

import ecdsa
import requests

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from .managers import PushApplicationManager

VAPID_KEY_STATUS_CHOICES = (
    ('pending', 'pending'),
    ('valid', 'valid'),
    ('invalid', 'invalid'),
    ('recording', 'recording')
)


def generate_jws_key_token():
    return uuid.uuid4()


def extract_public_key(key_data):
    """
    See https://github.com/mozilla-services/autopush/blob/
    89208a7c96b8edf00dae41bc744ccd505a483c64/autopush/utils.py#L111-L133
    A public key may come in several flavors. Attempt to extract the
    valid key bits from keys doing minimal validation checks.
    This is mostly a result of libs like WebCrypto prefixing data to "raw"
    keys, and the ecdsa library not really providing helpful errors.
    :param key_data: the raw-ish key we're going to try and process
    :returns: the raw key data.
    :raises: ValueError for unknown or poorly formatted keys.
    """
    # key data is actually a raw coordinate pair
    key_len = len(key_data)
    if key_len == 64:
        return key_data
    # Key format is "raw"
    if key_len == 65 and key_data[0] == '\x04':
        return key_data[-64:]
    # key format is "spki"
    if key_len == 88 and key_data[:3] == '0V0':
        return key_data[-64:]
    raise ValueError("Unknown public key format specified")


class PushApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    vapid_key = models.CharField(
        blank=True, max_length=255,
        help_text="VAPID p256ecdsa value; url-safe base-64 encoded."
    )
    vapid_key_status = models.CharField(max_length=255,
                                        default='pending',
                                        choices=VAPID_KEY_STATUS_CHOICES)
    vapid_key_token = models.CharField(max_length=255,
                                       editable=False,
                                       default=generate_jws_key_token)
    validated = models.DateTimeField(blank=True, null=True)

    objects = PushApplicationManager()

    def __unicode__(self):
        return "%s: %s" % (self.user.username, self.name)

    def validate_vapid_key(self, encrypted_token):
        try:
            key_data = urlsafe_b64decode(self.vapid_key)
            key_string = extract_public_key(key_data)
            verifying_key = ecdsa.VerifyingKey.from_string(
                key_string,
                curve=ecdsa.NIST256p
            )
            if (verifying_key.verify(encrypted_token,
                                     str(self.vapid_key_token))):
                self.vapid_key_status = 'valid'
                self.validated = timezone.make_aware(
                    datetime.now(),
                    timezone.get_current_timezone()
                )
                self.save()
                self.start_recording()
        except ecdsa.BadSignatureError:
            self.vapid_key_status = 'invalid'
            self.save()

    def start_recording(self):
        try:
            post_resp = self.post_key_to_autopush()
            if post_resp['status'] == 'success':
                self.vapid_key_status = 'recording'
                self.save()
        except requests.ConnectionError:
            # TODO: When post_key_to_autopush rasies ConnectionError ..
            pass

    def post_key_to_autopush(self):
        resp = requests.post(
            getattr(settings, 'AUTOPUSH_KEYS_ENDPOINT', '')
        )
        return resp.json()
