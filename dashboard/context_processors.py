from django.conf import settings


def conf_settings(request):
    return {'settings': settings}
