from apscheduler.schedulers.blocking import BlockingScheduler

from django.core.management import call_command


schedule = BlockingScheduler()


@schedule.scheduled_job('interval', minutes=3)
def start_recording_push_apps():
    call_command('start_recording_push_apps')


@schedule.scheduled_job('interval', minutes=3)
def validate_domain_authorizations():
    call_command('validate_domain_authorizations')


def run():
    try:
        schedule.start()
    except (KeyboardInterrupt, SystemExit):
        pass
