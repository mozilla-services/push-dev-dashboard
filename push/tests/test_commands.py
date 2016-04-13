from django.core.management import call_command
from django.test import TestCase

import fudge
from model_mommy import mommy

from ..models import PushApplication
from . import MESSAGES_API_POST_RESPONSE


class StartRecordingPushApplicationIntegrationTest(TestCase):
    @fudge.patch('push.models.PushApplication.post_key_to_api')
    def test_calls_task_calls_model_method_posts(self, post_key_to_api):
        valid_push_app = mommy.make(PushApplication, vapid_key_status='valid')
        post_key_to_api.expects_call().returns(MESSAGES_API_POST_RESPONSE)

        call_command('start_recording_push_apps')
        recording_push_app = PushApplication.objects.get(pk=valid_push_app.pk)
        self.assertEqual('recording', recording_push_app.vapid_key_status)
