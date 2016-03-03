from django.conf.urls import url

from push.views import PushApplicationDetails, ValidatePushApplication

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$',
        PushApplicationDetails.as_view(),
        name='push.details'),

    url(r'^(?P<pk>[0-9]+)/validate/$',
        ValidatePushApplication.as_view(),
        name='push.validate'),
]
