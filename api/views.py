from django.contrib import messages
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
        self.add_message()
        # redirect home after creating object
        return HttpResponseRedirect(reverse('home'))


class DomainAuthorizationViewSet(HomeAfterCreateModelViewSet):
    queryset = DomainAuthorization.objects.all()
    serializer_class = DomainAuthorizationSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def add_message(self):
        messages.success(self.request._request,
                         "Domain Added. Please add the token "
                         "value as a TXT record of your DNS.")


class PushApplicationViewSet(HomeAfterCreateModelViewSet):
    queryset = PushApplication.objects.all()
    serializer_class = PushApplicationSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def add_message(self):
        messages.success(self.request._request,
                         "Push Application Added. Please verify your signing "
                         "key.")
