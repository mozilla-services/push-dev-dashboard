from django.conf.urls import patterns, url, include

from rest_framework import routers

from .views import DomainAuthorizationViewSet


router = routers.DefaultRouter()
router.register(r'domains', DomainAuthorizationViewSet)

urlpatterns = patterns(
    '',
    url(r'^', include(router.urls))
)
