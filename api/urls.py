from django.conf.urls import patterns, url, include

from rest_framework import routers

from .views import DomainAuthorizationViewSet, PushApplicationViewSet


router = routers.DefaultRouter()
router.register(r'domains', DomainAuthorizationViewSet)
router.register(r'push-apps', PushApplicationViewSet)

urlpatterns = patterns(
    '',
    url(r'^', include(router.urls))
)
