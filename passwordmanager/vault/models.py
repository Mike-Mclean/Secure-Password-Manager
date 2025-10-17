from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class VaultItem(models.Model):
    """
    Model for encrypted string (vault item)
    the backend only receives the encrypted data and the algorithm used to encrypt it.
    The frontend handles the encryption/decryption using the user's master password at time
    of creation/retrieval
    """

    # Unique identifier for the vault item
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vault_items")

    title = models.CharField(
        max_length=255, help_text="Descriptive title for the vault item"
    )

    encrypted_data = models.TextField(help_text="Base64 encoded encrypted string")

    # TODO: this should be an enum/choices?
    encryption_algorithm = models.CharField(
        max_length=50, default="AES-256-CBC", help_text="Algorithm used for encryption"
    )

    ITEM_TYPES = [
        ("password", "Password"),
        ("note", "Secure Note"),
        ("other", "Other"),
    ]

    item_type = models.CharField(max_length=20, choices=ITEM_TYPES, default="password")

    description = models.TextField(
        blank=True, help_text="Optional description for the vault item"
    )

    created_at = models.DateTimeField(
        default=timezone.now, help_text="When the item was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True, help_text="When the item was last updated"
    )

    last_accessed = models.DateTimeField(
        null=True, blank=True, help_text="When the item was last accessed"
    )

    expires_at = models.DateTimeField(
        null=True, blank=True, help_text="When the item expires (optional)"
    )

    soft_deleted = models.BooleanField(default=False, help_text="Soft delete flag")

    class Meta:
        ordering = ["-updated_at", "-created_at"]
        verbose_name = "Vault Item"
        verbose_name_plural = "Vault Items"
        indexes = [
            models.Index(fields=["user", "soft_deleted"]),
            models.Index(fields=["user", "item_type"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    def is_expired(self):
        """Check if the vault item has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def mark_accessed(self):
        """Update the last_accessed timestamp."""
        self.last_accessed = timezone.now()
        self.save(update_fields=["last_accessed"])

    def soft_delete(self):
        """Soft delete the vault item."""
        self.soft_deleted = True
        self.save(update_fields=["soft_deleted"])

    def restore(self):
        """Restore a soft-deleted vault item."""
        self.soft_deleted = False
        self.save(update_fields=["soft_deleted"])


class VaultItemHistory(models.Model):
    """
    Model to track changes to vault items
    """

    vault_item = models.ForeignKey(
        VaultItem, on_delete=models.CASCADE, related_name="history"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="vault_item_history"
    )
    action = models.CharField(max_length=50, help_text="Action performed on the item")
    details = models.JSONField(
        blank=True, null=True, help_text="Additional details about the action"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Vault Item History"
        verbose_name_plural = "Vault Item Histories"

    def __str__(self):
        return f"{self.action} by {self.user.username} on {self.vault_item.title}"
