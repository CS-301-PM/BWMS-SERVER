from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Approval
from .serializers import ApprovalSerializer, ApprovalStatusUpdateSerializer
from .permissions import IsAssignedApprover, IsCorrectRoleForStage
from authentication.models import User

class ApprovalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing the approval workflow.
    List: Shows approvals relevant to the current user's role and assignments.
    Update: Allows an assigned approver to approve/reject their stage.
    """
    serializer_class = ApprovalSerializer
    permission_classes = [IsAuthenticated, IsCorrectRoleForStage]

    def get_queryset(self):
        """Return approvals that the current user is allowed to see and act upon."""
        user = self.request.user
        role_stage_map = {
            User.Role.STORES_MANAGER: Approval.Stage.STORES,
            User.Role.PROCUREMENT_OFFICER: Approval.Stage.PROCUREMENT,
            User.Role.CFO: Approval.Stage.CFO,
        }

        # If user is an admin, show all approvals
        if user.role == User.Role.ADMIN:
            return Approval.objects.all()

        # If user's role is not in the map, return empty queryset
        if user.role not in role_stage_map:
            return Approval.objects.none()

        # For approvers, show approvals for their stage where they are the assigned approver
        user_stage = role_stage_map[user.role]
        return Approval.objects.filter(stage=user_stage, approver=user)

    def perform_create(self, serializer):
        """Automatically set the approver to the current user."""
        serializer.save(approver=self.request.user)

    @action(detail=True, methods=['patch'], permission_classes=[IsAssignedApprover])
    def decide(self, request, pk=None):
        """Custom action for an approver to make a decision on their stage."""
        approval = self.get_object()

        if approval.status != Approval.Status.PENDING:
            return Response({'error': 'This approval stage has already been decided.'},
                          status=status.HTTP_400_BAD_REQUEST)

        serializer = ApprovalStatusUpdateSerializer(approval, data=request.data)
        if serializer.is_valid():
            serializer.save()

            # --- REAL BLOCKCHAIN INTEGRATION ---
            try:
                from blockchain.utils import log_approval_to_blockchain
                blockchain_log = log_approval_to_blockchain(approval)
                
                if blockchain_log:
                    print(f"✅ Successfully logged to blockchain. Tx Hash: {blockchain_log.transaction_hash}")
                    # You could also update the response to include the tx hash
                else:
                    print("❌ Blockchain logging failed. Check blockchain connection.")
                    # Consider how you want to handle blockchain failures
                    # You might want to revert the approval status change
                    
            except Exception as e:
                print(f"❌ Blockchain integration error: {e}")
                # Log the error but don't necessarily fail the request
            # --- END BLOCKCHAIN INTEGRATION ---

            return Response(ApprovalSerializer(approval).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=False, methods=['get'])
    def my_pending_approvals(self, request):
        """Custom endpoint to list all pending approvals assigned to the current user."""
        pending_approvals = self.get_queryset().filter(status=Approval.Status.PENDING)
        serializer = self.get_serializer(pending_approvals, many=True)
        return Response(serializer.data)