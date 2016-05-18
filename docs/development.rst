Development
===========

Requirements
------------

* `python`_ 2.7, `virtualenv`_, `pip`_ for app server
* `npm`_ for front-end testing

.. _python: https://www.python.org/
.. _virtualenv: http://docs.python-guide.org/en/latest/dev/virtualenvs/
.. _pip: https://pip.readthedocs.org/en/latest/
.. _npm: https://www.npmjs.com/


Install Locally
---------------

#. `Clone`_ and change to the directory::

    git clone git@github.com:mozilla-services/push-dev-dashboard.git
    cd push-dev-dashboard

#. Create and activate a `virtual environment`_ (Can also use `virtualenvwrapper`_)::

    virtualenv env
    source env/bin/activate

#. `Install requirements`_::

    pip install -r requirements-dev.txt
    npm install
    npm link stylus yuglify

#. Source the ``.env`` file to set environment config vars (Can also use `autoenv`_)::

    source .env

#. `Migrate`_ DB tables ::

    python manage.py migrate

#. `Create a superuser`_::

    python manage.py createsuperuser

.. _Clone: http://git-scm.com/book/en/Git-Basics-Getting-a-Git-Repository#Cloning-an-Existing-Repository
.. _Install requirements: http://pip.readthedocs.org/en/latest/user_guide.html#requirements-files
.. _Migrate: https://docs.djangoproject.com/en/1.9/topics/migrations/
.. _Create a superuser: https://docs.djangoproject.com/en/1.9/ref/django-admin/#django-admin-createsuperuser


Run it
------

#. Source the ``.env`` file to set environment config vars (Can also use `autoenv`_)::

    source .env

#. Activate the `virtual environment`_ (Can also use `virtualenvwrapper`_)::

    source env/bin/activate

#. Run it::

    python manage.py runserver


.. _Enable Firefox Accounts Auth:

Enable Firefox Accounts Auth
----------------------------

To enable Firefox Accounts authentication, you can use our local development
OAuth client app.

#. `Add a django-allauth social app`_ for Firefox Accounts (Log in as the
   superuser account you created):

   * Provider: Firefox Accounts
   * Name: fxa
   * Client id: 7a4cd4ca0fb1b5c9
   * Secret key: c10059ba24e6715a1b6f2c80f1cc398fb6a39ca18bc7554e894b36ea85b88eeb
   * Sites: example.com -> Chosen sites

#. `Log out of the admin account`_

#. Sign in with a Firefox Account at http://127.0.0.1:8000.

.. _Add a django-allauth social app: http://127.0.0.1:8000/admin/socialaccount/socialapp/add/
.. _Log out of the admin account: http://127.0.0.1:8000/admin/logout/

Run in production mode
----------------------

Follow these steps to emulate production (for example, to test compressed
assets). Run all commands from the project root.

#. Stop ``runserver`` if it's already running
#. In .env, set ``DJANGO_DEBUG`` to ``False``
#. Run ``python manage.py collectstatic``
#. Install `stunnel`_
    * Mac: ``brew install stunnel``
#. Run this command to generate a local cert and key for stunnel (you can use
   the default values for all prompts):
   ``openssl req -new -x509 -days 9999 -nodes -out stunnel/stunnel.pem -keyout stunnel/stunnel.pem``
#. Run ``stunnel stunnel/dev_https``
#. In another terminal, run ``HTTPS=1 python manage.py runserver 127.0.0.1:5000``
#. Go to https://127.0.0.1:8443 to confirm the certificate exception and browse
   the site

.. _stunnel: https://www.stunnel.org/index.html

Run the Tests
-------------

Back-end python tests
~~~~~~~~~~~~~~~~~~~~~

#. Install test requirements::

    pip install -r requirements-test.txt

#. Run the test suites::

    python manage.py test

Front-end style tests
~~~~~~~~~~~~~~~~~~~~~

#. Install test requirements::

    npm install

#. Run the test suites::

    npm test

Selenium/Integration tests
~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Install test requirements::

    pip install -r requirements-test.txt

#. Set environment variables::

    export DJANGO_DEBUG_TOOLBAR=False
    export TESTING_WEBDRIVER_TIMEOUT=10
    export TESTING_FXA_ACCOUNT_EMAIL=tester@test.com
    export TESTING_FXA_ACCOUNT_PASSWORD=testpass
    export TESTING_SITE=http://127.0.0.1:8000
    export TESTING_PUSH_SERVER_URL=wss://benpushstack-1704054003.dev.mozaws.net/

   * **Required** ``DJANGO_DEBUG_TOOLBAR`` - The django debug toolbar interferes with
     selenium clicking on the sign-in button; disable it.
   * **Required** ``TESTING_WEBDRIVER_TIMEOUT`` - Number of seconds selenium/Firefox will
     wait before timing out. Default is ``0`` which skips selenium test.
   * **Required** ``TESTING_FXA_ACCOUNT_EMAIL`` - Email of Firefox Account to use
     during tests.
   * **Required** ``TESTING_FXA_ACCOUNT_PASSWORD`` - Password of Firefox Account
     to use during tests.
   * ``TESTING_SITE`` - The dashboard domain/site that selenium/Firefox will
     use. Default is ``http://127.0.0.1:8000``
   * ``TESTING_PUSH_SERVER_URL`` - The ``dom.push.serverURL`` that
     selenium/Firefox will use. Default is the Firefox default:
     ``wss://push.services.mozilla.com/``
     *Note*: Make sure the `Push Messages API`_ server in
     ``PUSH_MESSAGES_API_ENDPOINT`` matches this push server.

#. Run the test suites::

    python manage.py test

.. _Push Messages API: https://github.com/mozilla-services/push-messages

Working on Docs
---------------
Install doc requirements::

    pip install -r requirements-docs.txt

Building the docs is easy::

    cd docs
    sphinx-build . html

Read the beautiful docs::

    open html/index.html


.. _Update translations:

Updating Translations
---------------------

#. Run ``makemessages`` to make updated ``django.po`` files::

    python manage.py makemessages --keep-pot

#. Commit the updates to git::

    git add locale
    git commit -m "Updating translations {YYYY-MM-DD}"


Adding a Translation
--------------------
#. First, `Update translations`_

#. Make the new ``{locale}`` directory for the new language::

    mkdir locale/{locale}

#. Run ``makemessages`` to make the ``django.po`` file for it::

    python manage.py makemessages -l {locale}

#. Add the new directory to git::

    git add locale/{locale}
    git commit -m "Adding {locale} locale"


What to work on
---------------

We have `Issues`_.

.. _Issues: https://github.com/mozilla-services/push-dev-dashboard/issues

.. _virtual environment: http://docs.python-guide.org/en/latest/dev/virtualenvs/
.. _virtualenvwrapper: https://pypi.python.org/pypi/virtualenvwrapper
.. _autoenv: https://github.com/kennethreitz/autoenv
