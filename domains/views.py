from rest_framework.viewsets import ModelViewSet

from .models import DomainAuthorization
from .serializers import DomainAuthorizationSerializer


# Create your views here.
class DomainAuthorizationViewSet(ModelViewSet):
    queryset = DomainAuthorization.objects.all()
    serializer_class = DomainAuthorizationSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
