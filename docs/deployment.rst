Deployment
==========

push-dev-dashboard is designed with `12-factor app philosophy`_, so you can
easily deploy your changes to your own app.


Deploy onto Deis
----------------

Note: Mozilla used to run our own Deis cluster, but it has been shut down. The
following instructions should work to deploy the code to your own Deis cluster.

#. `Install the deis client`_.

#. `Install deis on AWS`_.

#. Create the application::

    deis create dev-dashboard-username

#. Push code to the deis remote::

    git push deis master

#. `Create an RDS Postgres instance`_ in us-east-1 with default settings except:

   * DB Instance Class: db.t2.micro
   * Allocated Storag: 5 GB
   * VPC: vpc-9c2b0ef8

#. In the RDS Instance configuration details, click the "Security Groups".
   (Usually something like "rds-launch-wizard-N (sg-abcdef123)")

#. In the security group, under the "Inbound" tab, change the source to allow
   the deis cluster hosts.

#. Set the ``DATABASE_URL`` environment variable to match the RDS DB::

    deis config:set DATABASE_URL=postgres://username:password@endpoint/dbname

#. Migrate DB tables on the new RDS instance::

    deis run python manage.py migrate

#. Dock to app instance to create a superuser::

    deisctl dock dev-dashboard-username
    /app/.heroku/python/bin/python manage.py createsuperuser

#. Open the new deis app::

    deis open

.. _Create an RDS Postgres instance: https://console.aws.amazon.com/rds/home?region=us-east-1#launch-dbinstance:ct=dashboard:
.. _Install the deis client: http://docs.deis.io/en/latest/using_deis/install-client.html
.. _Install deis on AWS: http://docs.deis.io/en/latest/installing_deis/aws/


Enable Firefox Accounts Auth on your Deis app
---------------------------------------------

To enable Firefox Account sign-ins on your Deis app, you will need to create
your own Firefox Accounts OAuth Client for your app domain.

#. Go to `register your own Firefox Accounts OAuth Client`_:

    * Client name: dev-dashboard-username
    * Redirect URI: https://<your-push-dev-dashboard-app-on-deis-domain>/accounts/fxa/login/callback/
    * Trusted Mozilla Client: **CHECKED**

   Be sure to copy the client secret - you can't see it again.

#. Go to https://<your-push-dev-dashboard-app-on-deis-domain>/admin/socialaccount/socialapp/add/
   to :ref:`enable Firefox Accounts Auth` like a local machine; this time using your own new Firefox Accounts OAuth Client ID and Secret

#. Sign in at https://<your-push-dev-dashboard-app-on-deis-domain>/ with a Firefox
   Account.


.. _12-factor app philosophy: http://12factor.net/
.. _register your own Firefox Accounts OAuth Client: https://oauth-stable.dev.lcip.org/console/client/register
