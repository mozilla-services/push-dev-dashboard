from django.forms import ModelForm
from django.test import TestCase

from ..forms import DomainAuthForm
from ..models import DomainAuthorization


class DomainAuthFormTestCase(TestCase):
    def test_form_meta_properties(self):
        form = DomainAuthForm()
        self.assertIsInstance(form, ModelForm)
        self.assertEquals(DomainAuthorization, form.Meta.model)
        self.assertIn('domain', form.Meta.fields)
