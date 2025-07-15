from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import StockItem, StockRequest
from .serializers import StockItemSerializer, StockRequestSerializer
from django.db.models import Count, Sum
from rest_framework.views import APIView
from django.core.exceptions import PermissionDenied
from .blockchain_service import BlockchainLogger

class StockRequestViewSet(viewsets.ModelViewSet):
    queryset = StockRequest.objects.all()
    serializer_class = StockRequestSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.user_type != 'MANAGER':
            return Response(
                {"error": "Only managers can approve/reject requests"},
                status=status.HTTP_403_FORBIDDEN
            )

        new_status = request.data.get('status')
        if new_status not in ['APPROVED', 'REJECTED']:
            return Response(
                {"error": "Invalid status"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        instance.status = new_status
        instance.save()
        
        # TODO: Add blockchain logging here
        return Response({"status": "Request updated"})
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        new_status = request.data.get('status')
        
        if new_status == 'APPROVED':
            # Log to blockchain
            logger = BlockchainLogger()
            tx_hash = logger.log_approval(
                instance.id,
                instance.item.id,
                instance.quantity
            )
            instance.tx_hash = tx_hash
        
        instance.status = new_status
        instance.save()
        return Response({"status": "Request updated"})


class DashboardStats(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.user_type not in ['ADMIN', 'MANAGER']:
            return Response(
                {"error": "Unauthorized"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        stats = {
            'total_items': StockItem.objects.count(),
            'total_quantity': StockItem.objects.aggregate(Sum('quantity'))['quantity__sum'],
            'pending_requests': StockRequest.objects.filter(status='PENDING').count(),
            'approved_requests': StockRequest.objects.filter(status='APPROVED').count(),
            'rejected_requests': StockRequest.objects.filter(status='REJECTED').count(),
        }
        return Response(stats)

class StockItemViewSet(viewsets.ModelViewSet):
    queryset = StockItem.objects.all()
    serializer_class = StockItemSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        if self.request.user.user_type not in ['ADMIN', 'MANAGER']:
            raise PermissionDenied("Only admins/managers can update stock")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.user_type not in ['ADMIN', 'MANAGER']:
            raise PermissionDenied("Only admins/managers can delete stock")
        instance.delete()