from django.conf.urls import url

import push.views as push_views

urlpatterns = [
    url(r'^$',
        push_views.PushApplicationLanding.as_view(),
        name="push.landing"),

    url(r'^apps/$',
        push_views.PushApplications.as_view(),
        name='push.applications'),

    url(r'^apps/(?P<pk>[0-9]+)/$',
        push_views.PushApplicationDetails.as_view(),
        name='push.details'),

    url(r'^apps/(?P<pk>[0-9]+)/validate/$',
        push_views.ValidatePushApplication.as_view(),
        name='push.validate'),
]
