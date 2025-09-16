from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from utils.encryption_utils import EncryptedField

class User(AbstractUser):
    """
    Custom User model for CBU Central Stores Management System.
    Replaces the default Django User model.
    """
     # Encrypted fields
    _phone_number = models.CharField(max_length=20, blank=True, null=True)
    _personal_email = models.CharField(max_length=255, blank=True, null=True)
    
    # Properties for encrypted fields
    phone_number = EncryptedField('_phone_number')
    personal_email = EncryptedField('_personal_email')
    class Role(models.TextChoices):
        STORES_MANAGER = 'STORES_MANAGER', _('Stores Manager')
        PROCUREMENT_OFFICER = 'PROCUREMENT_OFFICER', _('Procurement Officer')
        CFO = 'CFO', _('Chief Finance Officer')
        DEPARTMENT_DEAN = 'DEPARTMENT_DEAN', _('Department Dean')
        ADMIN = 'ADMIN', _('System Admin') # Off-chain admin role

    # The role field is mandatory for every user
    role = models.CharField(max_length=20, choices=Role.choices)
    
    # Additional fields can be added here later (e.g., department, phone number)
    # For now, role is sufficient for RBAC.
    blockchain_address = models.CharField(
        max_length=42,  # Ethereum address length
        blank=True,
        null=True,
        verbose_name=_('Blockchain Address'),
        help_text=_('Ethereum address for blockchain interactions')
    )
    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"

    # Define unique related_names for groups and user_permissions to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="custom_user_set",  # Changed from default 'user_set'
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="custom_user_set",  # Changed from default 'user_set'
        related_query_name="user",
    )