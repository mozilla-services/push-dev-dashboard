Run-book
========

push-dev-dashboard is written as a monolithic django application with 2
processes. It's written with 12 factor methodology, so it is configured almost
entirely by environment variables.

`Travis CI`_ is used for unit, docs, l10n, and coding style tests before code
lands in master.

`Circle CI`_ is used to build docker containers for deployment.

`Jenkins`_ is used to run the selenium integration tests on deployments to the
stage and production servers.

.. _Travis CI: https://travis-ci.org/mozilla-services/push-dev-dashboard
.. _Circle CI: https://circleci.com/gh/mozilla-services/push-dev-dashboard
.. _Jenkins: https://services-qa-jenkins.stage.mozaws.net:8443/job/push-dashboard_e2e-test_prod/


Processes
---------

Web
~~~

The web process is a django web app run by gunicorn. It is defined as the
``CMD`` instruction in the ``Dockerfile``.

clock
~~~~~

The clock process is a python script run by the ``django_extensions``
``runscript`` command defined in ``Procfile``. It uses ``APScheduler`` to call
the ``start_recording_push_apps`` django command.


Environment Variables
---------------------

* **REQUIRED** ``DATABASE_URL`` - database connection url. See the ``dj-database-url``
  `URL schema`_ reference
* **REQUIRED** ``PUSH_MESSAGES_API_ENDPOINT`` - endpoint for `Push Messages API`_.
* **REQUIRED** ``FXA_OAUTH_ENDPOINT`` - endpoint for FxA oauth provider. See
  the ``django-allauth`` `Firefox Accounts`_ reference. 
* **REQUIRED** ``FXA_PROFILE_ENDPOINT`` - endpoint for FxA profile. See the
  ``django-allauth`` `Firefox Accounts`_ reference. 


.. _URL schema: https://github.com/kennethreitz/dj-database-url#url-schema
.. _Push Messages API: https://github.com/mozilla-services/push-messages
.. _Firefox Accounts: https://django-allauth.readthedocs.io/en/latest/providers.html#firefox-accounts
