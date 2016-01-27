"""Views for Firefox Accounts OAuth endpoints."""
from django.conf import settings

from allauth.socialaccount.providers.fxa.views import \
    FirefoxAccountsOAuth2Adapter as BaseAdapter
from allauth.socialaccount.providers.fxa.provider import \
    FirefoxAccountsProvider
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2LoginView, OAuth2CallbackView)


FXA_CONFIG = getattr(settings, 'SOCIALACCOUNT_PROVIDERS', {}).get('fxa', {})


class FirefoxAccountsOAuth2Adapter(BaseAdapter):
    provider_id = FirefoxAccountsProvider.id

    @property
    def access_token_url(self):
        return FXA_CONFIG.get('OAUTH_ENDPOINT', '') + '/token'

    @property
    def authorize_url(self):
        return FXA_CONFIG.get('OAUTH_ENDPOINT', '') + '/authorization'

    @property
    def profile_url(self):
        return FXA_CONFIG.get('PROFILE_ENDPOINT', '')


oauth2_login = OAuth2LoginView.adapter_view(FirefoxAccountsOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(FirefoxAccountsOAuth2Adapter)
