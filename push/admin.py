from django.contrib import admin

from .models import PushApplication


admin.site.register(PushApplication, admin.ModelAdmin)
