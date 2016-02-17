from django.forms import ModelForm

from .models import DomainAuthorization


class DomainAuthForm(ModelForm):
    class Meta:
        model = DomainAuthorization
        fields = ['domain', ]
