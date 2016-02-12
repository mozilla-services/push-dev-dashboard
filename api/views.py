from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from rest_framework.viewsets import ModelViewSet

from domains.models import DomainAuthorization
from push.models import PushApplication

from .serializers import (DomainAuthorizationSerializer,
                          PushApplicationSerializer)


class HomeAfterCreateModelViewSet(ModelViewSet):
    def create(self, request):
        super(HomeAfterCreateModelViewSet, self).create(request)
        # redirect home after creating DomainAuthorization
        return HttpResponseRedirect(reverse('home'))


class DomainAuthorizationViewSet(HomeAfterCreateModelViewSet):
    queryset = DomainAuthorization.objects.all()
    serializer_class = DomainAuthorizationSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class PushApplicationViewSet(HomeAfterCreateModelViewSet):
    queryset = PushApplication.objects.all()
    serializer_class = PushApplicationSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
