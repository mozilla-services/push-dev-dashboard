Development
===========

Requirements
------------

* `python`_


Install Locally
---------------

#. `Clone`_ and change to the directory::

    git clone git@github.com:groovecoder/push-dev-dashboard.git
    cd push-dev-dashboard

#. Create and activate a `virtual environment`_::

    virtualenv env
    source env/bin/activate

#. `Install requirements`_::

    pip install -r requirements.txt

#. `Migrate`_ DB tables ::

    ./manage.py migrate

#. `Create a superuser`_::

   ./manage.py createsuperuser


.. _python: https://www.python.org/
.. _Clone: http://git-scm.com/book/en/Git-Basics-Getting-a-Git-Repository#Cloning-an-Existing-Repository
.. _virtual environment: http://docs.python-guide.org/en/latest/dev/virtualenvs/
.. _Install requirements: http://pip.readthedocs.org/en/latest/user_guide.html#requirements-files
.. _Create a superuser: https://docs.djangoproject.com/en/1.7/ref/django-admin/#django-admin-createsuperuser


.. _Enable Firefox Accounts Auth:

Enable Firefox Accounts Auth
----------------------------

To enable Firefox Accounts authentication, you can use our local development
OAuth client app.

`Add a django-allauth social app`_ for Firefox Accounts:

* Provider: Firefox Accounts
* Name: fxa
* Client id: 7a4cd4ca0fb1b5c9
* Secret key: c10059ba24e6715a1b6f2c80f1cc398fb6a39ca18bc7554e894b36ea85b88eeb
* Sites: example.com -> Chosen sites

Now you can sign in with a Firefox Account at https://127.0.0.1:8000.

.. _Add a django-allauth social app: https://127.0.0.1:8000/admin/socialaccount/socialapp/add/


Run the Tests
-------------
Running the test suite is easy::

    ./manage.py test -s --noinput --logging-clear-handlers


Working on Docs
---------------
Install dev requirements::

    pip install -r docs/requirements.txt

Building the docs is easy::

    cd docs
    sphinx-build . html

Read the beautiful docs::

    open html/index.html


What to work on
---------------

We have `Issues`_.

.. _Issues: https://github.com/groovecoder/push-dev-dashboard/issues
