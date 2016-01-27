"""dashboard override of FirefoxAccountsProvider."""
from allauth.socialaccount import providers
from allauth.socialaccount.providers.fxa.provider import (
    FirefoxAccountsProvider as BaseProvider)


class FirefoxAccountsProvider(BaseProvider):
    package = 'dashboard.socialaccount.providers.fxa'


providers.registry.register(FirefoxAccountsProvider)
