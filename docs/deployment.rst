Deployment
==========

moz-dev-dash is designed with `12-factor app philosophy`_, so you can easily
deploy your changes to your own app.


Deploy your own (on Mozilla Deis)
---------------------------------

#. `Install the deis client`_.

#. `Register`_/login with the Mozilla Deis controller::

    deis register http://deis.deis.dev.mozaws.net
    deis auth:login http://deis.deis.dev.mozaws.net

#. Add your public key::

    deis keys:add

#. Create the application::

    deis create dev-dashboard-username

#. Push code to the deis remote::

    git push deis master

#. `Request a dev IAM account from Mozilla Cloud Ops`_ to create your RDS
   Postgres instance in the Mozilla account.

#. `Create an RDS Postgres instance`_ in us-east-1 with default settings except:

   * DB Instance Class: db.t2.micro
   * Allocated Storag: 5 GB
   * VPC: vpc-9c2b0ef8

#. In the RDS Instance configuration details, click the "Security Groups".
   (Usually something like "rds-launch-wizard-N (sg-abcdef123)")

#. In the security group, under the "Inbound" tab, change the source to allow
   the deis cluster hosts::

    10.21.0.0/16

#. Set the ``DATABASE_URL`` environment variable to match the RDS DB::

    deis config:set DATABASE_URL=postgres://username:password@endpoint/dbname

#. Migrate DB tables on the new RDS instance::

    deis run python manage.py migrate

#. Dock to app instance to create a superuser::

    deisctl dock dev-dashboard-username
    /app/.heroku/python/bin/python manage.py createsuperuser

#. Open the new deis app::

    deis open

.. _Request a dev IAM account from Mozilla Cloud Ops: https://mana.mozilla.org/wiki/display/SVCOPS/Requesting+A+Dev+IAM+account+from+Cloud+Operations
.. _Create an RDS Postgres instance: https://console.aws.amazon.com/rds/home?region=us-east-1#launch-dbinstance:ct=dashboard:
.. _Install the deis client: http://docs.deis.io/en/latest/using_deis/install-client.html
.. _Register: http://docs.deis.io/en/latest/using_deis/register-user.html


Enable Firefox Accounts Auth on your Deis app
---------------------------------------------

To enable Firefox Account sign-ins on your Deis app, you will need to create
your own Firefox Accounts OAuth Client for your app domain.

#. Go to `register your own Firefox Accounts OAuth Client`_:

    * Client name: moz-dev-dash-username
    * Redirect URI: http://dev-dashboard-username.deis.dev.mozaws.net/accounts/fxa/login/callback/
    * Trusted Mozilla Client: **CHECKED**

   Be sure to copy the client secret - you can't see it again.

#. Go to http://dev-dashboard-username.deis.dev.mozaws.net//admin/socialaccount/socialapp/add/
   to :ref:`enable Firefox Accounts Auth` like a local machine; this time using your own new Firefox Accounts OAuth Client ID and Secret

#. Sign in at http://dev-dashboard.deis.dev.mozaws.net/ with a Firefox
   Account.


.. _12-factor app philosophy: http://12factor.net/
.. _register your own Firefox Accounts OAuth Client: https://oauth-stable.dev.lcip.org/console/client/register

.. _git hooks: http://git-scm.com/book/en/Customizing-Git-Git-Hooks
