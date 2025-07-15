from django.db import models
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