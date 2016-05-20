Testing
=======

Back-end python tests
---------------------

#. Install test requirements::

    pip install -r requirements-test.txt

#. Run the test suites::

    python manage.py test

Back-end style tests
--------------------

#. Install test requirements::

    pip install flake8

#. Run the test suites::

    flake8 .

Front-end style tests
---------------------

#. Install test requirements::

    npm install

#. Run the test suites::

    npm test

Translation lint tests
----------------------

#. Install test requirements::

    pip install -r requirements-l10n.txt

#. Run the test suites::

    cd locale
    dennis-cmd lint .

Selenium/Integration tests
--------------------------

#. Install test requirements::

    pip install -r requirements-test.txt

#. Set environment variables in ``.env`` file::

    DJANGO_DEBUG_TOOLBAR=False
    TESTING_WEBDRIVER_TIMEOUT=10
    TESTING_FXA_ACCOUNT_EMAIL=tester@test.com
    TESTING_FXA_ACCOUNT_PASSWORD=testpass

   * **Required** ``DJANGO_DEBUG_TOOLBAR`` - The django debug toolbar interferes with
     selenium clicking on the sign-in button; disable it. *NOTE*: Make sure you
     restart the django process.
   * **Required** ``TESTING_WEBDRIVER_TIMEOUT`` - Number of seconds selenium/Firefox will
     wait before timing out. Default is ``0`` which skips selenium test.
   * **Required** ``TESTING_FXA_ACCOUNT_EMAIL`` - Email of Firefox Account to use
     during tests.
   * **Required** ``TESTING_FXA_ACCOUNT_PASSWORD`` - Password of Firefox Account
     to use during tests.
   * ``TESTING_SITE`` - The dashboard domain/site that selenium/Firefox will
     use. Default is ``http://127.0.0.1:8000``
   * ``TEST_PUSH_SERVER_URL`` - The ``dom.push.serverURL`` that
     selenium/Firefox will use. Default is the dev environment:
     ``wss://benpushstack-1704054003.dev.mozaws.net/``
     *Note*: Make sure the `Push Messages API`_ server in
     ``PUSH_MESSAGES_API_ENDPOINT`` matches this push server.

#. Run the test suites::

    python manage.py test

.. _Push Messages API: https://github.com/mozilla-services/push-messages
