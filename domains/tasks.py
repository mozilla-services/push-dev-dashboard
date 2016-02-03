from datetime import datetime

from decouple import config
from dnslib.dns import DNSRecord, DNSQuestion, QTYPE

from .models import DomainAuthorization


# Default: OpenDNS
DNS_VALIDATION_SERVER = config('DNS_VALIDATION_SERVER', '208.67.222.222')


# TODO: decorate with celery.task
def validate_domain_authorizations(status='pending'):
    domain_authorizations = DomainAuthorization.objects.filter(
        status='pending'
    )
    for auth in domain_authorizations:
        if auth.type == 'dns':
            txt_record = auth.token + '.' + auth.domain
            q = DNSRecord(q=DNSQuestion(txt_record, getattr(QTYPE, 'TXT')))
            record_pkt = q.send(DNS_VALIDATION_SERVER, 53)
            record = DNSRecord.parse(record_pkt)
            if str(record.a.rdata).strip('"') == auth.token:
                auth.status = 'valid'
                auth.validated = datetime.now()
                # TODO: determine a good value for auth.expires
                auth.save()
