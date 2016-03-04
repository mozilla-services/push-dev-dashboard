from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from domains.forms import DomainAuthForm
from domains.models import DomainAuthorization
from push.forms import PushAppForm, VapidValidationForm
from push.models import PushApplication


class PushApplicationLanding(TemplateView):
    template_name = 'push/landing.html'


class PushApplications(LoginRequiredMixin, TemplateView):
    template_name = 'push/applications.html'

    def get_context_data(self, **kwargs):
        context = super(PushApplications, self).get_context_data(**kwargs)
        context['domain_auth_form'] = DomainAuthForm()
        context['push_app_form'] = PushAppForm()
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


class PushApplicationDetails(UserPassesTestMixin, TemplateView):
    template_name = 'push/details.html'
    raise_exception = True

    def test_func(self):
        push_app = get_object_or_404(PushApplication, pk=self.kwargs['pk'])
        return push_app.created_by(self.request.user)

    def get_context_data(self, **kwargs):
        push_app = get_object_or_404(PushApplication, pk=self.kwargs['pk'])

        context = super(PushApplicationDetails,
                        self).get_context_data(**kwargs)
        context.update({
            'id': push_app.id,
            'name': push_app.name,
            'vapid_key_status': push_app.vapid_key_status,
            'vapid_key_token': push_app.vapid_key_token,
        })

        return context


class ValidatePushApplication(UserPassesTestMixin, TemplateView):
    template_name = 'push/validate.html'
    raise_exception = True

    def test_func(self):
        push_app = get_object_or_404(PushApplication, pk=self.kwargs['pk'])
        return push_app.created_by(self.request.user)

    def get_context_data(self, **kwargs):
        push_app = get_object_or_404(PushApplication, pk=self.kwargs['pk'])

        context = super(ValidatePushApplication,
                        self).get_context_data(**kwargs)
        context.update({
            'id': push_app.id,
            'vapid_key_token': push_app.vapid_key_token,
            'vapid_validation_form': VapidValidationForm(),
        })

        return context

    def post(self, request, pk, *args, **kwargs):
        push_app = get_object_or_404(PushApplication, pk=pk)
        push_app.validate_vapid_key(request.POST["signed_token"])
        # TODO: add message
        return redirect('push.details', pk=pk)
