from rest_framework.viewsets import ModelViewSet

from domains.models import DomainAuthorization
from push.models import PushApplication

from .serializers import (DomainAuthorizationSerializer,
                          PushApplicationSerializer)


# Create your views here.
class DomainAuthorizationViewSet(ModelViewSet):
    queryset = DomainAuthorization.objects.all()
    serializer_class = DomainAuthorizationSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class PushApplicationViewSet(ModelViewSet):
    queryset = PushApplication.objects.all()
    serializer_class = PushApplicationSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
