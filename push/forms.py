from django.forms import ModelForm, Form, CharField

from .models import PushApplication


class PushAppForm(ModelForm):
    class Meta:
        model = PushApplication
        fields = ['name', 'vapid_key']


class VapidValidationForm(Form):
    signed_token = CharField()
