from django.db import models


class PushApplicationManager(models.Manager):
    def need_recording(self):
        return super(PushApplicationManager, self).get_queryset().filter(
            vapid_key_status='valid'
        )
