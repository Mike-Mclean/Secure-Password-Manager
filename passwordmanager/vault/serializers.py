from rest_framework import serializers
from vault.models import VaultItem, VaultItemHistory
from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema_field


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for Django User with minimal fields.
    """

    class Meta:
        model = User
        fields = ["id", "username", "email", "date_joined"]
        read_only_fields = ["id", "username", "email", "date_joined"]


class VaultItemSerializer(serializers.ModelSerializer):
    """
    Serializer for VaultItem model.
    """

    user_info = UserSerializer(source="user", read_only=True)
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = VaultItem
        fields = [
            "id",
            "user_info",
            "title",
            "encrypted_data",
            "encryption_algorithm",
            "item_type",
            "description",
            "created_at",
            "updated_at",
            "last_accessed",
            "expires_at",
            "soft_deleted",
            "is_expired",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "last_accessed",
            "user_info",
            "is_expired",
        ]

    @extend_schema_field(serializers.BooleanField())
    def get_is_expired(self, obj):
        """Calculate if the vault item is expired."""
        return obj.is_expired()

    def validate_title(self, value):
        """Ensure title is not empty."""
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value.strip()

    def validate_encrypted_data(self, value):
        """Basic validation for encrypted data."""
        if not value:
            raise serializers.ValidationError("Encrypted data cannot be empty.")
        return value

    def create(self, validated_data):
        """Override create to set the User from request."""
        # Get the User from the request (set by Django authentication)
        user = self.context["request"].user
        validated_data["user"] = user

        vault_item = VaultItem.objects.create(**validated_data)
        VaultItemHistory.objects.create(
            vault_item=vault_item,
            user=user,
            action="created",
            details={"created_via": "api"},
        )

        return vault_item


class VaultItemListSerializer(serializers.ModelSerializer):
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = VaultItem
        fields = [
            "id",
            "title",
            "item_type",
            "description",
            "created_at",
            "updated_at",
            "last_accessed",
            "soft_deleted",
            "is_expired",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "last_accessed",
            "is_expired",
        ]

    def get_is_expired(self, obj):
        return obj.is_expired()


class VaultItemHistorySerializer(serializers.ModelSerializer):
    user_info = UserSerializer(source="user", read_only=True)
    vault_item_title = serializers.CharField(source="vault_item.title", read_only=True)

    class Meta:
        model = VaultItemHistory
        fields = [
            "id",
            "vault_item",
            "vault_item_title",
            "user_info",
            "action",
            "details",
            "timestamp",
        ]
        read_only_fields = ["id", "user_info", "vault_item_title", "timestamp"]
