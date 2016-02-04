from __future__ import unicode_literals
from datetime import datetime, timedelta
import uuid

from decouple import config
from dnslib.dns import DNSRecord, DNSQuestion, QTYPE

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from .managers import DomainAuthorizationManager


# Default: OpenDNS
DNS_VALIDATION_SERVER = config('DNS_VALIDATION_SERVER', '208.67.222.222')

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

    objects = DomainAuthorizationManager()

    def __unicode__(self):
        return "%s: %s" % (self.user.username, self.domain)

    def save(self, *args, **kwargs):
        self.token = uuid.uuid5(uuid.NAMESPACE_DNS, str(self.domain))
        super(DomainAuthorization, self).save(*args, **kwargs)

    def get_dns_txt_record(self):
        txt_record = self.token + '.' + self.domain
        q = DNSRecord(q=DNSQuestion(txt_record, getattr(QTYPE, 'TXT')))
        record_pkt = q.send(DNS_VALIDATION_SERVER, 53)
        record = DNSRecord.parse(record_pkt)
        return record

    def validate(self):
        if self.type == 'dns':
            record = self.get_dns_txt_record()
            if str(record.a.rdata).strip('"') == self.token:
                self.status = 'valid'
                self.validated = timezone.make_aware(
                    datetime.now(),
                    timezone.get_current_timezone()
                )
                self.expires = timezone.make_aware(
                    datetime.now() + timedelta(1),
                    timezone.get_current_timezone()
                )
                self.save()
