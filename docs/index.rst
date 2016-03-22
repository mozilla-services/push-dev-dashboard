.. moz-dev-dash documentation master file, created by
   sphinx-quickstart on Sun May 18 11:17:00 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome
=======

moz-dev-dash is the code for Mozilla Developer Services dashboard. It combines:

* `Firefox Accounts`_ Authentication (via `django-allauth`_)
* (Soon) Domain Verification (via ?)
* `Mozilla Push Service`_ metrics

.. _Firefox Accounts: https://support.mozilla.org/en-US/kb/access-mozilla-services-firefox-accounts
.. _django-allauth: https://github.com/pennersr/django-allauth
.. _Mozilla Push Service: https://autopush.readthedocs.org/en/latest/


Resources
---------
.. image:: https://travis-ci.org/mozilla-services/push-dev-dashboard.png?branch=master
   :target: https://travis-ci.org/mozilla-services/push-dev-dashboard
   :alt: Travis-CI Build Status
.. image:: https://coveralls.io/repos/mozilla-services/push-dev-dashboard/badge.png
    :target: https://coveralls.io/r/mozilla-services/push-dev-dashboard
.. image:: https://requires.io/github/mozilla-services/push-dev-dashboard/requirements.png?branch=master
   :target: https://requires.io/github/mozilla-services/push-dev-dashboard/requirements/?branch=master
   :alt: Requirements Status

:Code:          https://github.com/mozilla-services/push-dev-dashboard
:License:       MPL2
:Documentation: http://push-dev-dashboard.readthedocs.org/
:Issues:        https://github.com/mozilla-services/push-dev-dashboard/issues
:IRC:           irc://irc.mozilla.org/mds
:Mailing list:  https://lists.mozilla.org/listinfo/mds-public
:Servers:       http://dev-dashboard.deis.dev.mozaws.net/ (stage)


Contents
--------

.. toctree::
   :maxdepth: 2

   development
   deployment
