from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import DepartmentRequest
from .serializers import DepartmentRequestSerializer, DepartmentRequestStatusUpdateSerializer
from .permissions import IsDepartmentDeanOrReadOnly, CanViewAllRequests
from authentication.models import User

class DepartmentRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and creating Department Requests.
    """
    serializer_class = DepartmentRequestSerializer
    permission_classes = [IsAuthenticated, CanViewAllRequests, IsDepartmentDeanOrReadOnly]

    def get_queryset(self):
        """Return all requests for Managers/Admins, only user's requests for Deans."""
        user = self.request.user
        
        if user.role in [User.Role.STORES_MANAGER, User.Role.PROCUREMENT_OFFICER, 
                        User.Role.CFO, User.Role.ADMIN]:
            # Stores Managers and other approvers can see all requests
            return DepartmentRequest.objects.all().order_by('-date_requested')
        elif user.role == User.Role.DEPARTMENT_DEAN:
            # Deans can only see their own requests
            return DepartmentRequest.objects.filter(requested_by=user).order_by('-date_requested')
        else:
            # Other roles see nothing
            return DepartmentRequest.objects.none()

    def perform_create(self, serializer):
        """Automatically set the requesting user to the current user."""
        serializer.save(requested_by=self.request.user)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        """Custom action for Stores Manager to approve/reject a request."""
        request_obj = self.get_object()
        user = self.request.user

        # Check if user is authorized to update status (Stores Manager or Admin)
        if user.role not in [User.Role.STORES_MANAGER, User.Role.ADMIN]:
            return Response({'error': 'Permission denied. Only Stores Managers can update status.'}, 
                          status=status.HTTP_403_FORBIDDEN)

        # Check if the request is still pending
        if request_obj.status != DepartmentRequest.Status.PENDING:
            return Response({'error': 'This request has already been processed.'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        serializer = DepartmentRequestStatusUpdateSerializer(request_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # TODO: Trigger blockchain logging here
            # TODO: Automatically create approval chain if status is APPROVED
            
            return Response(DepartmentRequestSerializer(request_obj).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Custom endpoint to get all pending requests."""
        user = request.user
        
        if user.role in [User.Role.STORES_MANAGER, User.Role.ADMIN]:
            # Stores Managers see all pending requests
            pending_requests = DepartmentRequest.objects.filter(status=DepartmentRequest.Status.PENDING)
        elif user.role == User.Role.DEPARTMENT_DEAN:
            # Deans see only their pending requests
            pending_requests = DepartmentRequest.objects.filter(
                requested_by=user, 
                status=DepartmentRequest.Status.PENDING
            )
        else:
            pending_requests = DepartmentRequest.objects.none()
            
        serializer = self.get_serializer(pending_requests, many=True)
        return Response(serializer.data)