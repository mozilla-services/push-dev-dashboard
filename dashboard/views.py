from django.http import HttpResponse
from django.views.generic import TemplateView, View


class Home(TemplateView):
    template_name = 'dashboard/home.html'


class Login(TemplateView):
    template_name = 'dashboard/login.html'


class PermissionDenied(TemplateView):
    template_name = 'dashboard/errors/403.html'


class InternalServerError(TemplateView):
    template_name = 'dashboard/errors/500.html'


class Heartbeat(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('OK')


class PushTestPage(TemplateView):
    template_name = 'dashboard/push_test_page.html'
