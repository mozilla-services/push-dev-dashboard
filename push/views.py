from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView

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

    def post(self, request, *args, **kwargs):
        push_app_form = PushAppForm(request.POST)
        if push_app_form.is_valid():
            new_push_app = push_app_form.save(commit=False)
            new_push_app.user = request.user
            new_push_app.save()
            messages.success(self.request, _("Added push application."))
            return redirect('push.validation', pk=str(new_push_app.id))
        else:
            for field in push_app_form.errors.keys():
                for message in push_app_form.errors[field]:
                    messages.error(request, message)
            return redirect('push.list')


class UserOwnsPushAppMixin(UserPassesTestMixin):
    def test_func(self):
        push_app = get_object_or_404(PushApplication, pk=self.kwargs['pk'])
        return push_app.created_by(self.request.user)

    def get_context_data(self, **kwargs):
        push_app = get_object_or_404(PushApplication, pk=kwargs['pk'])
        context = dict({'app': push_app})
        return context


class Details(UserOwnsPushAppMixin, TemplateView):
    template_name = 'push/details.html'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(Details, self).get_context_data(**kwargs)
        # TODO: refactor push_app.get_messages() from view into template
        push_app = context['app']
        app_messages = {'messages': []}
        try:
            app_messages = push_app.get_messages()
        except MessagesAPIError as e:
            messages.warning(self.request, e.message)
        context.update({'app_messages': app_messages['messages']})

        return context


class Validation(UserOwnsPushAppMixin, TemplateView):
    template_name = 'push/validation.html'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(Validation, self).get_context_data(**kwargs)
        context.update({
            'vapid_validation_form': VapidValidationForm(),
        })

        return context

    def post(self, request, pk, *args, **kwargs):
        push_app = get_object_or_404(PushApplication, pk=pk)
        push_app.validate_vapid_key(request.POST["signed_token"])
        if push_app.valid():
            messages.success(self.request, _("VAPID Key validated.") + " " +
                             _("It may take up to 10 minutes to start "
                               "recording."))
        elif push_app.invalid():
            messages.warning(self.request, _("Invalid signature."))
        return redirect('push.details', pk=pk)


class Deletion(UserOwnsPushAppMixin, TemplateView):
    template_name = 'push/deletion.html'
    raise_exception = True

    def post(self, request, pk, *args, **kwargs):
        push_app = get_object_or_404(PushApplication, pk=pk)
        num_deleted, app_deleted = push_app.delete()
        if num_deleted == 1:
            messages.success(self.request, _("Application deleted."))
        else:
            messages.warning(self.request, _("Unable to delete application."))
        return redirect('push.list')
