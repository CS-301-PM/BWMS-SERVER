from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPES = [
        ('ADMIN', 'Admin'),
        ('MANAGER', 'Manager'),
        ('CENTRAL_STAFF', 'Central Store Staff'),
        ('DEPT_STAFF', 'Department Staff'),
        ('SUPPLIER', 'Supplier'),
    ]
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    department = models.CharField(max_length=100, blank=True)
    wallet_address = models.CharField(max_length=42, blank=True)  # Ethereum address field

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"