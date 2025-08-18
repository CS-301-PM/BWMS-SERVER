from django.db import models
from accounts.models import CustomUser
from inventory.blockchain_service import BlockchainService
from accounts.models import CustomUser

class StockItem(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=100)
    last_updated = models.DateTimeField(auto_now=True)
    eth_contract_id = models.CharField(max_length=66, blank=True)  # Blockchain reference

    def __str__(self):
        return f"{self.name} (Qty: {self.quantity})"

class StockRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    item = models.ForeignKey(StockItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    requester = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    tx_hash = models.CharField(max_length=66, blank=True)  # Blockchain tx
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request #{self.id} - {self.item.name}"
    department = models.CharField(max_length=100)  # Add department tracking
    urgent = models.BooleanField(default=False)    # Add priority flag

# Additional models for stock movements and damage reports
class StockMovement(models.Model):
    """UC-018: Track physical relocation of inventory"""
    item = models.ForeignKey('StockItem', on_delete=models.PROTECT)
    from_location = models.CharField(max_length=100)
    to_location = models.CharField(max_length=100)
    moved_by = models.ForeignKey('accounts.CustomUser', on_delete=models.PROTECT)
    tx_hash = models.CharField(max_length=66, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.tx_hash:
            tx_data = {
                'item_id': self.item.id,
                'from': self.from_location,
                'to': self.to_location,
                'staff': self.moved_by.wallet_address
            }
            self.tx_hash = BlockchainService().log_transaction('stock_movement', tx_data)
        super().save(*args, **kwargs)

class DamageReport(models.Model):
    """UC-019: Damage reporting system"""
    item = models.ForeignKey(StockItem, on_delete=models.PROTECT)
    reporter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reported_damages')
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=[
        ('minor', 'Minor'),
        ('major', 'Major'),
        ('critical', 'Critical')
    ])
    tx_hash = models.CharField(max_length=66, blank=True)
    resolved = models.BooleanField(default=False)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Damage Report #{self.id} - {self.item.name}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Damage Report'
        verbose_name_plural = 'Damage Reports'

class SupplierDelivery(models.Model):
    supplier = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    items = models.ManyToManyField('StockItem', through='DeliveryItem')
    delivery_date = models.DateTimeField(auto_now_add=True)
    tx_hash = models.CharField(max_length=66, blank=True)
    verified = models.BooleanField(default=False)

class DeliveryItem(models.Model):
    delivery = models.ForeignKey(SupplierDelivery, on_delete=models.CASCADE)
    item = models.ForeignKey('StockItem', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()