from django.core.management.base import BaseCommand

from ...tasks import validate_domain_authorizations


class Command(BaseCommand):
    help = 'Validate all pending domain authorizations.'

    def handle(self, *args, **kwargs):
        validate_domain_authorizations()
