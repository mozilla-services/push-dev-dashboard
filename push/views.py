from django.views.generic import TemplateView

from push.models import PushApplication
from push.forms import VapidValidationForm


class PushApplicationDetails(TemplateView):
    template_name = 'push/details.html'

    def get_context_data(self, **kwargs):
        push_app = PushApplication.objects.get(pk=self.kwargs['pk'])

        context = super(PushApplicationDetails,
                        self).get_context_data(**kwargs)
        context.update({
            'id': push_app.id,
            'name': push_app.name,
            'vapid_key_status': push_app.vapid_key_status,
            'vapid_key_token': push_app.vapid_key_token,
        })

        return context


class ValidatePushApplication(TemplateView):
    template_name = 'push/validate.html'

    def get_context_data(self, **kwargs):
        push_app = PushApplication.objects.get(pk=self.kwargs['pk'])

        context = super(ValidatePushApplication,
                        self).get_context_data(**kwargs)
        context.update({
            'id': push_app.id,
            'vapid_key_token': push_app.vapid_key_token,
            'vapid_validation_form': VapidValidationForm(),
        })

        return context
