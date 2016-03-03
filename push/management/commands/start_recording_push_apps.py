from django.core.management.base import BaseCommand

from ...tasks import start_recording_push_apps


class Command(BaseCommand):
    help = 'Start recording all valid push app keys.'

    def handle(self, *args, **kwargs):
        start_recording_push_apps()
