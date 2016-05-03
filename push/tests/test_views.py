import fudge
from model_mommy import mommy

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import Http404
from django.test import Client, TestCase

from dashboard.tests import UrlTestsFor200

from ..forms import PushAppForm
from ..models import PushApplication, MessagesAPIError
from ..views import (Deletion, Details, Landing, List, UserOwnsPushAppMixin,
                     Validation)
from . import MESSAGES_API_RESPONSE_JSON_MESSAGES


class PushUrlTestsFor200(UrlTestsFor200):
    def setUp(self):
        super(PushUrlTestsFor200, self).setUp()
        self.app = mommy.make(PushApplication,
                              user=self.user,
                              vapid_key_status='pending')
        self.signed_out_urls = (
            '/en/push/',
        )
        self.signed_in_urls = (
            '/en/push/apps/',
            '/en/push/apps/%d/',
            '/en/push/apps/%d/validation/',
        )

    def assert_all_urls_200(self, urls):
        for url in urls:
            try:
                # try to interpolate the app.id when necessary
                url = url % self.app.id
            except TypeError:
                pass
            self.assert_url_200(url)


class UserOwnsPushAppMixinTest(TestCase):
    def test_func_404_unknown_pk(self):
        with self.assertRaises(Http404):
            mixin = UserOwnsPushAppMixin()
            mixin.kwargs = {'pk': 1}
            mixin.test_func()

    def test_func_false_if_not_users_app(self):
        user = mommy.make(User)
        other_user = mommy.make(User)
        app = mommy.make(PushApplication, user=user)
        mixin = UserOwnsPushAppMixin()
        mixin.request = fudge.Fake().has_attr(user=other_user)
        mixin.kwargs = {'pk': app.id}
        self.assertFalse(mixin.test_func())

    def test_true_if_users_app(self):
        user = mommy.make(User)
        app = mommy.make(PushApplication, user=user)
        mixin = UserOwnsPushAppMixin()
        mixin.request = fudge.Fake().has_attr(user=user)
        mixin.kwargs = {'pk': app.id}
        self.assertTrue(mixin.test_func())

    def test_adds_app_to_context_data(self):
        user = mommy.make(User)
        app = mommy.make(PushApplication, user=user)
        mixin = UserOwnsPushAppMixin()
        mixin.request = fudge.Fake().has_attr(user=user)
        context = mixin.get_context_data(pk=app.id)
        self.assertEqual(app, context['app'])


class PushViewGETTests(TestCase):
    def setUp(self):
        self.user = mommy.make(User)
        self.request = fudge.Fake().has_attr(user=self.user)

    def test_template_names(self):
        landing = Landing()
        listing = List()
        details = Details()
        validate = Validation()
        deletion = Deletion()
        self.assertIn('landing.html', landing.template_name)
        self.assertIn('list.html', listing.template_name)
        self.assertIn('details.html', details.template_name)
        self.assertIn('validation.html', validate.template_name)
        self.assertIn('deletion.html', deletion.template_name)

    def test_listing_context_form_and_apps_for_user(self):
        listing = List()
        listing.request = self.request

        context = listing.get_context_data()
        self.assertIsInstance(context['push_app_form'], PushAppForm)
        self.assertEqual(0, len(context['push_apps']))

        mommy.make(PushApplication, user=self.user)
        context = listing.get_context_data()
        self.assertEqual(self.user, context['push_apps'][0].user)

        other_user = mommy.make(User)
        mommy.make(PushApplication, user=other_user)
        context = listing.get_context_data()
        self.assertEqual(1, len(context['push_apps']))
        for app in context['push_apps']:
            self.assertEqual(self.user, app.user)
            self.assertNotEqual(other_user, app.user)

    @fudge.patch("push.views.get_object_or_404")
    def test_details_context_empty_messages(self,
                                            get_object_or_404):
        get_object_or_404.expects_call().returns(
            fudge.Fake().expects('get_messages').returns(
                {'messages': []}
            )
        )
        app = mommy.make(PushApplication, user=self.user)
        details = Details(pk=app.id)
        details.request = self.request

        context = details.get_context_data(pk=app.id)
        self.assertEqual(0, len(context['app_messages']))

    @fudge.patch("push.views.get_object_or_404")
    def test_details_context_with_messages(self,
                                           get_object_or_404):
        get_object_or_404.expects_call().returns(
            fudge.Fake().expects('get_messages').returns(
                {'messages': MESSAGES_API_RESPONSE_JSON_MESSAGES}
            )
        )
        app = mommy.make(PushApplication, user=self.user)
        details = Details(pk=app.id)
        details.request = self.request

        context = details.get_context_data(pk=app.id)
        self.assertEqual(2, len(context['app_messages']))

    @fudge.patch("push.views.get_object_or_404")
    @fudge.patch("push.views.messages")
    def test_details_context_with_MessagesAPIError_calls_warning(
        self, get_object_or_404, messages
    ):
        get_object_or_404.expects_call().returns(
            fudge.Fake().expects('get_messages').raises(
                MessagesAPIError('broken')
            )
        )
        messages.expects('warning')
        app = mommy.make(PushApplication, user=self.user)
        details = Details(pk=app.id)
        details.request = self.request

        context = details.get_context_data(pk=app.id)
        self.assertEqual(0, len(context['app_messages']))


class PushListIntegrationTests(TestCase):
    def setUp(self):
        super(PushListIntegrationTests, self).setUp()
        self.user = mommy.make(User)
        self.password = 'testpass'
        self.user.set_password(self.password)
        self.user.save()
        self.client = Client()
        self.client.login(username=self.user.username,
                          password=self.password)

    def _assert_redirect_to_list(self, resp):
        self.assertEqual(302, resp.status_code)
        self.assertEqual(reverse('push.list'), resp['Location'])

    @fudge.patch("push.views.messages")
    def test_list_post_adds_app_for_user_success_message(self, messages):
        messages.expects('success')
        resp = self.client.post(
            reverse('push.list'), {'name': 'test-post',
                                   'vapid_key': 'test-post'}
        )

        self.assertEqual(302, resp.status_code)
        push_app = PushApplication.objects.get(user=self.user)
        self.assertEqual(reverse('push.validation',
                                 kwargs={'pk': push_app.id}),
                         resp['Location'])

    @fudge.patch("push.views.messages")
    def test_list_post_invalid_doesnt_create_redirects_back_to_list(
        self,
        messages
    ):
        messages.expects('error')
        resp = self.client.post(
            reverse('push.list'), {'name2': 'test-post',
                                   'vapid_lock': 'test-post'}
        )

        self._assert_redirect_to_list(resp)

    @fudge.patch("push.views.messages")
    def test_list_post_dupe_doesnt_create_redirects_to_list_with_error(
        self,
        messages
    ):
        self.app = mommy.make(PushApplication,
                              user=self.user,
                              vapid_key='test')
        messages.expects('error')
        resp = self.client.post(
            reverse('push.list'), {'name': 'test-dupe',
                                   'vapid_key': 'test'}
        )

        self._assert_redirect_to_list(resp)

        # make sure non-dupe posts are still working
        messages.expects('success')
        resp = self.client.post(
            reverse('push.list'), {'name': 'test-non-dupe',
                                   'vapid_key': 'test-non-dupe'}
        )


class PushDeletionViewTests(TestCase):
    def setUp(self):
        self.user = mommy.make(User)
        self.app = mommy.make(PushApplication, user=self.user)
        self.request = fudge.Fake().has_attr(user=self.user)
        self.view = Deletion()
        self.view.request = self.request

    def test_post_unkown_pk_404(self):
        self.assertEqual(1, len(PushApplication.objects.all()))
        deletion = Deletion()
        with self.assertRaises(Http404):
            deletion.post(self.request, 9999)
        self.assertEqual(1, len(PushApplication.objects.all()))

    @fudge.patch("push.views.messages")
    def test_post_pk_deletes_and_redirects(self, messages):
        messages.expects('success')
        self.assertEqual(1, len(PushApplication.objects.all()))
        resp = self.view.post(self.request, self.app.id)
        self.assertEqual(0, len(PushApplication.objects.all()))
        self.assertEqual(302, resp.status_code)


class PushValidationViewTests(TestCase):
    def setUp(self):
        self.user = mommy.make(User)
        self.app = mommy.make(PushApplication, user=self.user)
        self.request = fudge.Fake().has_attr(user=self.user,
                                             POST={"signed_token": True})
        self.view = Validation()
        self.view.request = self.request

    def test_post_unkown_pk_404(self):
        self.assertEqual(1, len(PushApplication.objects.all()))
        with self.assertRaises(Http404):
            self.view.post(self.request, 9999)
        self.assertEqual(1, len(PushApplication.objects.all()))

    @fudge.patch("push.views.messages")
    @fudge.patch("push.views.get_object_or_404")
    def test_post_pk_valid_token_redirects_with_success(self,
                                                        messages,
                                                        get_object):
        messages.expects('success')
        (get_object.expects_call()
                   .returns_fake()
                   .expects("validate_vapid_key")
                   .expects("valid").returns(True))
        resp = self.view.post(self.request, self.app.id)
        self.assertEqual(302, resp.status_code)

    @fudge.patch("push.views.messages")
    @fudge.patch("push.views.get_object_or_404")
    def test_post_pk_invalid_token_redirects_with_warning(self,
                                                          messages,
                                                          get_object):
        messages.expects('warning')
        (get_object.expects_call()
                   .returns_fake()
                   .expects("validate_vapid_key")
                   .expects("valid").returns(False)
                   .expects("invalid").returns(True))
        resp = self.view.post(self.request, self.app.id)
        self.assertEqual(302, resp.status_code)
