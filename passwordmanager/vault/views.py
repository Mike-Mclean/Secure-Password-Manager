from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import VaultItem, VaultItemHistory
from .permissions import MFARequiredIfOptedIn
from .serializers import (
    VaultItemListSerializer,
    VaultItemHistorySerializer,
    VaultItemSerializer,
)


class VaultItemViewSet(viewsets.ModelViewSet):

    permission_classes = [permissions.IsAuthenticated, MFARequiredIfOptedIn]

    def get_serializer_class(self):
        if self.action == "list" or self.action == "deleted":
            return VaultItemListSerializer
        return VaultItemSerializer

    def get_queryset(self):
        """Return only the current user's vault items."""
        return VaultItem.objects.filter(
            user=self.request.user, soft_deleted=False
        ).order_by("-updated_at")

    def perform_create(self, serializer):
        """Automatically set the user when creating."""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Track access when updating."""
        instance = serializer.save()
        instance.mark_accessed()

    def retrieve(self, request, *args, **kwargs):
        """Track access when retrieving a single item."""
        instance = self.get_object()
        instance.mark_accessed()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def soft_delete(self, request, pk=None):
        """Soft delete a vault item."""
        vault_item = self.get_object()
        vault_item.soft_delete()

        VaultItemHistory.objects.create(
            vault_item=vault_item,
            user=request.user,
            action="deleted",
            details={"deleted_via": "api"},
        )

        return Response({"status": "deleted"})

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        """Restore a soft-deleted vault item."""
        vault_item = get_object_or_404(
            VaultItem, pk=pk, user=request.user, soft_deleted=True
        )
        vault_item.restore()

        VaultItemHistory.objects.create(
            vault_item=vault_item,
            user=request.user,
            action="restored",
            details={"restored_via": "api"},
        )

        return Response({"status": "restored"})

    @action(detail=False, methods=["get"])
    def deleted(self, request):
        """Get soft-deleted items."""
        deleted_items = VaultItem.objects.filter(user=request.user, soft_deleted=True)
        serializer = VaultItemListSerializer(deleted_items, many=True)
        return Response(serializer.data)


class VaultItemHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing vault item history (read-only).
    """

    permission_classes = [permissions.IsAuthenticated, MFARequiredIfOptedIn]
    serializer_class = VaultItemHistorySerializer

    def get_queryset(self):
        """Return history for user's vault items only."""
        vault_item_id = self.request.query_params.get("vault_item")

        queryset = VaultItemHistory.objects.filter(vault_item__user=self.request.user)

        if vault_item_id:
            queryset = queryset.filter(vault_item_id=vault_item_id)

        return queryset.order_by("-timestamp")
