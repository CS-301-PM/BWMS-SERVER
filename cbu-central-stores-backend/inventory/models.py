from django.db import models
from django.utils.translation import gettext_lazy as _

class Product(models.Model):
    """
    Model representing an item in the central stores inventory.
    """
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    qr_code_data = models.JSONField(blank=True, null=True)  # Stores data encoded in QR

    def save(self, *args, **kwargs):
        """Override save to generate QR code automatically."""
        is_new = self.pk is None
        
        super().save(*args, **kwargs)
        
        # Generate QR code for new products or when important data changes
        if is_new or not self.qr_code:
            from utils.qr_code_utils import generate_qr_code
            
            qr_data = {
                'product_id': self.id,
                'name': self.name,
                'category': self.category,
                'current_stock': self.quantity,
                'last_updated': self.date_updated.isoformat()
            }
            
            qr_path = generate_qr_code(qr_data, self.id)
            self.qr_code = qr_path
            self.qr_code_data = qr_data
            # Save again to update QR code field
            super().save(update_fields=['qr_code', 'qr_code_data'])
            
    class Category(models.TextChoices):
        OFFICE_SUPPLIES = 'OFFICE_SUPPLIES', _('Office Supplies')
        LAB_EQUIPMENT = 'LAB_EQUIPMENT', _('Laboratory Equipment')
        ICT_EQUIPMENT = 'ICT_EQUIPMENT', _('ICT Equipment')
        FURNITURE = 'FURNITURE', _('Furniture')
        CLEANING_MATERIALS = 'CLEANING_MATERIALS', _('Cleaning Materials')
        OTHERS = 'OTHERS', _('Others')

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHERS)
    quantity = models.PositiveIntegerField(default=0)
    # The quantity at which a low-stock alert should be triggered
    low_stock_threshold = models.PositiveIntegerField(default=5)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.quantity} in stock)"

    @property
    def is_low_stock(self):
        """Returns True if the current quantity is at or below the threshold."""
        return self.quantity <= self.low_stock_threshold

    class Meta:
        ordering = ['-date_updated']  # Show most recently updated items first