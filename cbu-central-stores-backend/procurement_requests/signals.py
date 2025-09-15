from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import DepartmentRequest
from approvals.models import Approval
from authentication.models import User

@receiver(post_save, sender=DepartmentRequest)
def create_approval_chain(sender, instance, created, **kwargs):
    """
    Signal to automatically create the approval chain when a DepartmentRequest
    is approved by the Stores Manager for the first time.
    """
    print(f"Signal triggered for request {instance.id}, created: {created}, status: {instance.status}")
    
    # If the request was just created, do nothing (wait for status update)
    if created:
        print("Request created, waiting for status update...")
        return

    # Check if the status was just changed to APPROVED by Stores
    if instance.status == DepartmentRequest.Status.APPROVED:
        print("Request approved by Stores, creating approval chain...")
        # Check if the approval chain already exists to avoid duplicates
        if instance.approvals.exists():
            print("Approval chain already exists, skipping...")
            return

        # Get or create default approvers for each stage
        try:
            stores_manager = User.objects.filter(role=User.Role.STORES_MANAGER).first()
            procurement_officer = User.objects.filter(role=User.Role.PROCUREMENT_OFFICER).first()
            cfo = User.objects.filter(role=User.Role.CFO).first()
            
            print(f"Stores Manager: {stores_manager}")
            print(f"Procurement Officer: {procurement_officer}") 
            print(f"CFO: {cfo}")

        except User.DoesNotExist:
            print("Approvers not setup yet")
            return

        # Create the three approval stages
        if stores_manager:
            Approval.objects.create(
                request=instance,
                stage=Approval.Stage.STORES,
                approver=stores_manager,
                status=Approval.Status.APPROVED, # Auto-approve the Stores stage
                comment="Automatically approved as part of request approval."
            )
            print("Created Stores approval")

        if procurement_officer:
            Approval.objects.create(
                request=instance,
                stage=Approval.Stage.PROCUREMENT,
                approver=procurement_officer
                # status defaults to PENDING
            )
            print("Created Procurement approval")

        if cfo:
            Approval.objects.create(
                request=instance,
                stage=Approval.Stage.CFO,
                approver=cfo
                # status defaults to PENDING
            )
            print("Created CFO approval")
            
        print("Approval chain created successfully!")