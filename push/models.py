from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


class PushApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    jws_key = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return "%s: %s" % (self.user.username, self.name)
