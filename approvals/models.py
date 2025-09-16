from django.db import models
from django.utils.translation import gettext_lazy as _
from authentication.models import User

class Approval(models.Model):
    """
    Model representing a single step in the 3-step approval workflow for a restock request.
    Each DepartmentRequest will have multiple Approval instances (one for each step).
    """

    class Stage(models.TextChoices):
        STORES = 'STORES', _('Stores Manager Approval')
        PROCUREMENT = 'PROCUREMENT', _('Procurement Officer Approval')
        CFO = 'CFO', _('CFO Approval')

    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')

    # Link to the original department request
    request = models.ForeignKey('procurement_requests.DepartmentRequest', on_delete=models.CASCADE, related_name='approvals')
    # Which stage of approval this record represents
    stage = models.CharField(max_length=15, choices=Stage.choices)
    # The user responsible for making a decision at this stage
    approver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approvals_given')
    # The decision made
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    # Mandatory comment/reason for the decision
    comment = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_stage_display()} - {self.status} by {self.approver.username} for Request #{self.request.id}"

    class Meta:
        # Ensure we only have one approval record per request per stage
        unique_together = ['request', 'stage']
        ordering = ['request', 'stage']  # Order by request ID and then stage