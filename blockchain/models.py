from django.db import models
from django.utils.translation import gettext_lazy as _
from inventory.models import Product
from procurement_requests.models import DepartmentRequest
from authentication.models import User

class BlockchainTransactionType(models.TextChoices):
    APPROVAL = 'APPROVAL', _('Approval Decision')
    DELIVERY = 'DELIVERY', _('Goods Delivered')
    RELOCATION = 'RELOCATION', _('Item Relocated')
    DAMAGE_REPORT = 'DAMAGE_REPORT', _('Damage Reported')

class BlockchainLog(models.Model):
    """
    Model to store a reference to any transaction logged on the blockchain.
    Links the on-chain transaction hash to an off-chain entity (Request or Product).
    """
    transaction_type = models.CharField(max_length=20, choices=BlockchainTransactionType.choices)
    transaction_hash = models.CharField(max_length=66, unique=True) # 0x prefix + 64 hex characters

    # Link to the relevant entity. One of these will be null.
    related_request = models.ForeignKey(DepartmentRequest, on_delete=models.CASCADE, null=True, blank=True, related_name='blockchain_logs')
    related_product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='blockchain_logs')

    initiated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_logged = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(null=True, blank=True) # Store function arguments or event data for easier off-chain querying

    class Meta:
        verbose_name = _('Blockchain Log')
        verbose_name_plural = _('Blockchain Logs')
        ordering = ['-date_logged']
        indexes = [
            models.Index(fields=['transaction_hash']),
            models.Index(fields=['transaction_type', 'date_logged']),
        ]

    def __str__(self):
        return f"{self.transaction_type} - {self.transaction_hash}"