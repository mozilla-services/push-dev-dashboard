import fudge
from model_mommy import mommy

from django.contrib.auth.models import User
from django.http import Http404
from django.test import TestCase

from dashboard.tests import UrlTestsFor200

from ..forms import PushAppForm
from ..models import PushApplication, MessagesAPIError
from ..views import Landing, List, Details, Validation, UserOwnsPushAppMixin
from . import messages_api_response_json_messages


class PushUrlTestsFor200(UrlTestsFor200):
    def setUp(self):
        super(PushUrlTestsFor200, self).setUp()
        self.app = mommy.make(PushApplication, user=self.user)
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


class PushViewTests(TestCase):
    def setUp(self):
        self.user = mommy.make(User)
        self.request = fudge.Fake().has_attr(user=self.user)

    def test_template_names(self):
        landing = Landing()
        listing = List()
        details = Details()
        validate = Validation()
        self.assertIn('landing.html', landing.template_name)
        self.assertIn('list.html', listing.template_name)
        self.assertIn('details.html', details.template_name)
        self.assertIn('validation.html', validate.template_name)

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
                {'messages': messages_api_response_json_messages}
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
