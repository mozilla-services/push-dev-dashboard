from datetime import datetime

from django.db import models


class DomainAuthorizationManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.expired_Q = models.Q(expires__lte=datetime.now())
        self.pending_Q = models.Q(status='pending')
        super(DomainAuthorizationManager, self).__init__(*args, **kwargs)

    def expired(self):
        return super(DomainAuthorizationManager, self).get_queryset().filter(
            self.expired_Q
        )

    def need_validation(self):
        return super(DomainAuthorizationManager, self).get_queryset().filter(
            self.expired_Q | self.pending_Q
        )
