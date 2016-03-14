from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from domains.forms import DomainAuthForm
from domains.models import DomainAuthorization
from push.forms import PushAppForm, VapidValidationForm
from push.models import PushApplication, MessagesAPIError


class Landing(TemplateView):
    template_name = 'push/landing.html'


class List(LoginRequiredMixin, TemplateView):
    template_name = 'push/list.html'

    def get_context_data(self, **kwargs):
        context = super(List, self).get_context_data(**kwargs)
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


class UserOwnsPushAppMixin(UserPassesTestMixin):
    def test_func(self):
        push_app = get_object_or_404(PushApplication, pk=self.kwargs['pk'])
        return push_app.created_by(self.request.user)


class Details(UserOwnsPushAppMixin, TemplateView):
    template_name = 'push/details.html'
    raise_exception = True

    def get_context_data(self, **kwargs):
        push_app = get_object_or_404(PushApplication, pk=kwargs['pk'])

        context = super(Details, self).get_context_data(**kwargs)
        app_messages = {'messages': []}
        try:
            app_messages = push_app.get_messages()
        except MessagesAPIError as e:
            messages.warning(self.request, e.message)
        context.update({
            'app': push_app,
            'app_messages': app_messages['messages']
        })

        return context


class Validation(UserOwnsPushAppMixin, TemplateView):
    template_name = 'push/validation.html'
    raise_exception = True

    def get_context_data(self, **kwargs):
        push_app = get_object_or_404(PushApplication, pk=self.kwargs['pk'])

        context = super(Validation, self).get_context_data(**kwargs)
        context.update({
            'app': push_app,
            'vapid_validation_form': VapidValidationForm(),
        })

        return context

    def post(self, request, pk, *args, **kwargs):
        push_app = get_object_or_404(PushApplication, pk=pk)
        push_app.validate_vapid_key(request.POST["signed_token"])
        if push_app.valid:
            messages.success(self.request, "VAPID Key validated.")
        elif push_app.invalid:
            messages.warning(self.request, "Invalid signature.")
        return redirect('push.details', pk=pk)
