from django.conf.urls import url

import push.views as push_views

urlpatterns = [
    url(r'^$', push_views.Landing.as_view(), name="push.landing"),

    url(r'^apps/$',
        push_views.List.as_view(),
        name='push.list'),

    url(r'^apps/(?P<pk>[0-9]+)/$', push_views.Details.as_view(),
        name='push.details'),

    url(r'^apps/(?P<pk>[0-9]+)/validation/$',
        push_views.Validation.as_view(),
        name='push.validation'),
]
