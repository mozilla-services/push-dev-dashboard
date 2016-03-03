from .models import PushApplication


# TODO: decorate with celery.task
def start_recording_push_apps():
    push_apps = PushApplication.objects.need_recording()
    for push_app in push_apps:
        push_app.start_recording()
