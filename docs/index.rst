.. push-dev-dashboard documentation master file, created by
   sphinx-quickstart on Sun May 18 11:17:00 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome
=======

push-dev-dashboard is the code for Mozilla Developer Services dashboard - where web
developers can manage how their web apps and sites use services like
`Mozilla Push Service`_.

.. _Mozilla Push Service: https://autopush.readthedocs.org/en/latest/


Resources
---------
.. image:: https://travis-ci.org/mozilla-services/push-dev-dashboard.png?branch=master
   :target: https://travis-ci.org/mozilla-services/push-dev-dashboard
   :alt: Travis-CI Build Status
.. image:: https://codecov.io/github/mozilla-services/push-dev-dashboard/coverage.svg?branch=master
    :target: https://codecov.io/github/mozilla-services/push-dev-dashboard?branch=master
.. image:: https://requires.io/github/mozilla-services/push-dev-dashboard/requirements.png?branch=master
   :target: https://requires.io/github/mozilla-services/push-dev-dashboard/requirements/?branch=master
   :alt: Requirements Status

:Code:          https://github.com/mozilla-services/push-dev-dashboard
:License:       MPL2
:Documentation: http://push-dev-dashboard.readthedocs.org/
:Issues:        https://github.com/mozilla-services/push-dev-dashboard/issues
:CI:            https://travis-ci.org/mozilla-services/push-dev-dashboard (unit
                tests)

                https://circleci.com/gh/mozilla-services/push-dev-dashboard
                (deployment artifacts)

                https://services-qa-jenkins.stage.mozaws.net:8443/job/push-dashboard_e2e-test_prod/ (selenium/integration tests)
:Servers:       https://pushdevdashboard-default.stage.mozaws.net/ (stage)
                https://push-dashboard.services.mozilla.com/ (prod)
:IRC:           irc://irc.mozilla.org/push

Contents
--------

.. toctree::
   :maxdepth: 2

   development
   testing
   deployment
   run
