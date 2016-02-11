from django.views.generic import TemplateView

from domains.models import DomainAuthorization
from push.models import PushApplication


class Home(TemplateView):
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        domains = None
        push_apps = None
        if (self.request.user.is_authenticated()):
            domains = DomainAuthorization.objects.filter(
                user=self.request.user
            )
            push_apps = PushApplication.objects.filter(user=self.request.user)
        context['domains'] = domains
        context['push_apps'] = push_apps
        return context
