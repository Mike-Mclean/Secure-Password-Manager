
# from django.contrib.auth import views as auth_views
from django.urls import path, include, re_path
from django.conf import settings

# from rest_framework import routers

urlpatterns = [
    path("vault/", include("vault.urls")),
    path("accounts/", include("accounts.urls", namespace="accounts")),
]

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
urlpatterns += [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]