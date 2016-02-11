from rest_framework import serializers

from domains.models import DomainAuthorization
from push.models import PushApplication


class DomainAuthorizationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = DomainAuthorization
        fields = ('id', 'user', 'domain', 'status', 'token', 'type',
                  'validated', 'expires')
        read_only_fields = ('id', 'user', 'status', 'token', 'type',
                            'validated', 'expires')


class PushApplicationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = PushApplication
        fields = ('id', 'user', 'name', 'jws_key')
