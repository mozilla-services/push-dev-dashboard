from django.views.generic import TemplateView

from domains.models import DomainAuthorization
from push.models import PushApplication


class Home(TemplateView):
    template_name = 'dashboard/home.html'


class Profile(TemplateView):
    template_name = 'dashboard/profile.html'

    def get_context_data(self, **kwargs):
        context = super(Profile, self).get_context_data(**kwargs)
        domains = DomainAuthorization.objects.filter(user=self.request.user)
        push_apps = PushApplication.objects.filter(user=self.request.user)
        context['domains'] = domains
        context['push_apps'] = push_apps
        return context
