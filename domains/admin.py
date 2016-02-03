from django.contrib import admin

from .models import DomainAuthorization


class DomainAuthorizationAdmin(admin.ModelAdmin):
    readonly_fields = ('token', 'validated', 'expires')


admin.site.register(DomainAuthorization, DomainAuthorizationAdmin)
