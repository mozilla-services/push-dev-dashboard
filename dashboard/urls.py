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
from django.contrib import admin

import dashboard.views as dashboard_views

handler403 = dashboard_views.PermissionDenied.as_view()
handler404 = dashboard_views.NotFound.as_view()
handler500 = dashboard_views.InternalServerError.as_view()

urlpatterns = [
    # our app urls
    url(r'^$', dashboard_views.Home.as_view(), name='home'),
    url(r'^api/docs/', include('rest_framework_swagger.urls')),
    url(r'^api/v1/', include('api.urls')),
    url(r'^push/', include('push.urls')),
    url(r'^accounts/login/$', dashboard_views.Login.as_view(), name='login'),

    # 3rd-party app urls
    url(r'^accounts/', include('allauth.urls')),

    # django urls
    url(r'^admin/', admin.site.urls),
]

# Make some error pages available under error/ for easier testing
if settings.DEBUG:
    urlpatterns += [
        url(r'^error/404/$', dashboard_views.NotFound.as_view()),
        url(r'^error/500/$', dashboard_views.InternalServerError.as_view()),
    ]
