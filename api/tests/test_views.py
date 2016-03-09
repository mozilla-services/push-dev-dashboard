from django.contrib.auth.models import User
from django.test import TestCase

import fudge
from model_mommy import mommy

from domains.models import DomainAuthorization
from push.models import PushApplication

from .. import serializers, views


class DomainAuthorizationViewSetTest(TestCase):
    def setUp(self):
        self.view = views.DomainAuthorizationViewSet()

    def test_attrs(self):
        self.assertIsInstance(self.view, views.ModelViewSet)
        self.assertEqual(DomainAuthorization, self.view.queryset.model)
        self.assertEqual(self.view.serializer_class,
                         serializers.DomainAuthorizationSerializer)

    def test_queryset_filters_to_users_own_objects(self):
        user1 = mommy.make(User)
        user2 = mommy.make(User)
        mommy.make(DomainAuthorization, user=user1)
        mommy.make(DomainAuthorization, user=user2)
        self.view.request = fudge.Fake().has_attr(user=user1)

        domain_auths = self.view.get_queryset()
        for domain_auth in domain_auths:
            self.assertEqual(domain_auth.user, user1)

        self.view.request = fudge.Fake().has_attr(user=user2)

        domain_auths = self.view.get_queryset()
        for domain_auth in domain_auths:
            self.assertEqual(domain_auth.user, user2)

    @fudge.patch('api.views.messages.success')
    def test_add_message_calls_messages_success(self, success):
        success.expects_call()
        self.view.request = fudge.Fake().has_attr(_request=None)
        self.view.add_message()


class PushApplicationViewSetTest(TestCase):
    def setUp(self):
        self.view = views.PushApplicationViewSet()

    def test_attrs(self):
        self.assertIsInstance(self.view, views.ModelViewSet)
        self.assertEqual(PushApplication, self.view.queryset.model)
        self.assertEqual(self.view.serializer_class,
                         serializers.PushApplicationSerializer)

    def test_queryset_filters_to_users_own_objects(self):
        user1 = mommy.make(User)
        user2 = mommy.make(User)
        mommy.make(PushApplication, user=user1)
        mommy.make(PushApplication, user=user2)
        self.view.request = fudge.Fake().has_attr(user=user1)

        push_apps = self.view.get_queryset()
        for push_app in push_apps:
            self.assertEqual(push_app.user, user1)

        self.view.request = fudge.Fake().has_attr(user=user2)

        push_apps = self.view.get_queryset()
        for push_app in push_apps:
            self.assertEqual(push_app.user, user2)

    @fudge.patch('api.views.messages.success')
    def test_add_message_calls_messages_success(self, success):
        success.expects_call()
        self.view.request = fudge.Fake().has_attr(_request=None)
        self.view.add_message()
