from __future__ import unicode_literals
import uuid

from django.contrib.auth.models import User
from django.db import models


AUTHORIZATION_STATUS_CHOICES = (
    ('unknown', 'unknown'),
    ('pending', 'pending'),
    ('processing', 'processing'),
    ('valid', 'valid'),
    ('invalid', 'invalid'),
    ('revoked', 'revoked')
)

AUTHORIZATION_TYPE_CHOICES = (
    ('simpleHttp', 'simpleHttp'),
    ('dns', 'dns')
)


class DomainAuthorization(models.Model):
    """ Represents a user's authorization of a domain. """
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    domain = models.CharField(max_length=255)
    status = models.CharField(max_length=255,
                              default='pending',
                              choices=AUTHORIZATION_STATUS_CHOICES)
    # TODO: maybe use django built-in UUIDField and default=callable
    token = models.CharField(max_length=255, editable=False)
    type = models.CharField(max_length=255,
                            default='dns',
                            choices=AUTHORIZATION_TYPE_CHOICES)
    validated = models.DateTimeField(blank=True, null=True)
    expires = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return "%s: %s" % (self.user.username, self.domain)

    def save(self, *args, **kwargs):
        self.token = uuid.uuid5(uuid.NAMESPACE_DNS, str(self.domain))
        super(DomainAuthorization, self).save(*args, **kwargs)
