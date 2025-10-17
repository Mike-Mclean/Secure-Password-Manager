from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"items", views.VaultItemViewSet, basename="vaultitem")
router.register(r"history", views.VaultItemHistoryViewSet, basename="vaultitemhistory")

urlpatterns = [
    path("", include(router.urls)),
]
