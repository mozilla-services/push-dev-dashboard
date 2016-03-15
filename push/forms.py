from django.forms import ModelForm, Form, CharField, TextInput

from .models import PushApplication


class PushAppForm(ModelForm):
    class Meta:
        model = PushApplication
        fields = ['name', 'vapid_key']
        widgets = {
            'name': TextInput(attrs={'required': True}),
            'vapid_key': TextInput(attrs={'required': True})
        }


class VapidValidationForm(Form):
    signed_token = CharField()
