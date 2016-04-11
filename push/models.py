from __future__ import unicode_literals
from base64 import urlsafe_b64decode
import uuid

import ecdsa
import requests

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .managers import PushApplicationManager

VAPID_KEY_STATUS_CHOICES = (
    ('pending', 'pending'),
    ('valid', 'valid'),
    ('invalid', 'invalid'),
    ('recording', 'recording')
)


class MessagesAPIError(Exception):
    def __init__(self, message, status_code=None):
        super(Exception, self).__init__(
            _("Error communicating with Push Messages API: %s") % message
        )
        self.status_code = status_code


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
    raise ValueError(_("Unknown public key format specified"))


def get_autopush_endpoint():
    endpoint = getattr(settings, 'PUSH_MESSAGES_API_ENDPOINT', None)
    if not endpoint:
        raise ImproperlyConfigured(
            _("Must set PUSH_MESSAGES_API_ENDPOINT env var.")
        )
    return endpoint


def push_messages_api_request(method, endpoint, json_data=None):
    try:
        resp = requests.request(method,
                                get_autopush_endpoint() + endpoint,
                                json=json_data,
                                timeout=settings.PUSH_MESSAGES_API_TIMEOUT)
    except requests.exceptions.RequestException as e:
        raise MessagesAPIError(e.message)
    if resp.status_code == 200:
        return resp.json()
    elif resp.status_code == 404:
        raise MessagesAPIError("404 at %s" % endpoint, resp.status_code)
    else:
        raise MessagesAPIError(
            # Translators: Error status code & content returned from an API
            _("Status: %(status)s; Content: %(content)s") %
            {'status': resp.status_code, 'content': resp.content}
        )


class PushApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    vapid_key = models.CharField(
        blank=False, max_length=255,
        help_text=_("VAPID p256ecdsa value; url-safe base-64 encoded.")
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

    def can_validate(self):
        return self.vapid_key_status in ['pending', 'invalid']

    def valid(self):
        return self.vapid_key_status in ['valid', 'recording']

    def invalid(self):
        return self.vapid_key_status == 'invalid'

    def recording(self):
        return self.vapid_key_status == 'recording'

    def validate_vapid_key(self, b64_signed_token):
        try:
            key_data = urlsafe_b64decode(str(self.vapid_key))
            key_string = extract_public_key(key_data)
            verifying_key = ecdsa.VerifyingKey.from_string(
                key_string,
                curve=ecdsa.NIST256p
            )
            signed_token = urlsafe_b64decode(str(b64_signed_token))
            if (verifying_key.verify(signed_token, str(self.vapid_key_token))):
                self.vapid_key_status = 'valid'
                self.validated = timezone.now()
                self.save()
                self.start_recording()
        except ecdsa.BadSignatureError:
            self.vapid_key_status = 'invalid'
            self.save()

    def start_recording(self):
        assert self.vapid_key_status == 'valid'
        post_resp_json = self.post_key_to_api()
        if post_resp_json['status'] == 'success':
            self.vapid_key_status = 'recording'
            self.save()

    def post_key_to_api(self):
        return push_messages_api_request('post',
                                         '/keys',
                                         {'public-key': self.vapid_key})

    def get_messages(self):
        try:
            resp_json = push_messages_api_request(
                'get',
                '/messages/%s' % self.vapid_key
            )
            return resp_json
        except MessagesAPIError as e:
            if e.status_code == 404:
                # 404 from messages API indicates that *ALL* Push Apps' keys
                # were lost. So, we need to reset all apps' vapid status to
                # 'valid', which will cause start_recording_push_apps to
                # re-POST *ALL* push apps' keys to messages API for recording
                PushApplication.objects.all().update(vapid_key_status='valid')
            else:
                raise MessagesAPIError(e.message)

    def created_by(self, user):
        return self.user == user
