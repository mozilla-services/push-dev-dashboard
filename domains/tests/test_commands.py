from django.core.management import call_command
from django.test import TestCase

import fudge
from model_mommy import mommy

from ..models import DomainAuthorization


class ValidateDomainAuthorizationsIntegrationTest(TestCase):
    # patch out the model DNS method
    @fudge.patch('domains.models.DomainAuthorization.get_dns_txt_record')
    def test_calls_task(self, get_dns_txt_record):
        da = mommy.make(DomainAuthorization, status='pending')
        get_dns_txt_record.expects_call().returns(
            fudge.Fake().has_attr(
                a=fudge.Fake().has_attr(
                    rdata='"%s"' % da.token
                )
            )
        )
        call_command('validate_domain_authorizations')
        da = DomainAuthorization.objects.get(pk=da.pk)
        self.assertEqual('valid', da.status)
