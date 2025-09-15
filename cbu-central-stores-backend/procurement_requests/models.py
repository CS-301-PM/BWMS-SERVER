from django.db import models
from django.utils.translation import gettext_lazy as _
from authentication.models import User
from inventory.models import Product

class DepartmentRequest(models.Model):
    """
    Model representing a request made by a Department Dean for a specific product.
    This is the initial request that starts the approval workflow.
    """

    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending Review by Stores')
        APPROVED = 'APPROVED', _('Approved by Stores')
        REJECTED = 'REJECTED', _('Rejected by Stores')
        # States for Procurement and CFO will be handled in the approvals app

    class Priority(models.TextChoices):
        LOW = 'LOW', _('Low')
        MEDIUM = 'MEDIUM', _('Medium')
        HIGH = 'HIGH', _('High')
        URGENT = 'URGENT', _('Urgent')

    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_requests')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='requests')
    quantity_requested = models.PositiveIntegerField()
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    reason = models.TextField(help_text="Justification for the request and its priority.")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    stores_comment = models.TextField(blank=True, help_text="Comments from the Stores Manager upon approval/rejection.")
    date_requested = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request #{self.id} for {self.product.name} by {self.requested_by.username}"

    class Meta:
        ordering = ['-date_requested']  # Show newest requests first