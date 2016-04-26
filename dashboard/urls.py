"""dashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin

import dashboard.views as dashboard_views

handler403 = dashboard_views.PermissionDenied.as_view()
handler500 = dashboard_views.InternalServerError.as_view()

urlpatterns = [
    # dockerflow healthcheck endpoints
    url(r'^%s$' % settings.HEALTHCHECK_URL,
        dashboard_views.Heartbeat.as_view(), name='heartbeat'),
    url(r'^%s$' % settings.LBHEALTHCHECK_URL,
        dashboard_views.Heartbeat.as_view(), name='lbheartbeat'),

    # 3rd-party app urls
    url(r'^accounts/', include('allauth.urls')),
    url(r'^api/docs/', include('rest_framework_swagger.urls')),

    # django urls
    url(r'^admin/', admin.site.urls),

    url(r'^api/v1/', include('api.urls')),
]

urlpatterns += i18n_patterns(
    # our app urls
    url(r'^$', dashboard_views.Home.as_view(), name='home'),
    url(r'^push/', include('push.urls')),
    url(r'^accounts/login/$', dashboard_views.Login.as_view(), name='login'),
)
