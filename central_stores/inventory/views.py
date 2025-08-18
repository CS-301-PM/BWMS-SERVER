from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import DamageReport, StockItem, StockMovement, StockRequest, SupplierDelivery
from .serializers import DamageReportSerializer, DepartmentRequestSerializer, StockItemSerializer, StockMovementSerializer, StockRequestSerializer, SupplierDeliverySerializer
from django.db.models import Count, Sum
from rest_framework.views import APIView
from django.core.exceptions import PermissionDenied
from .blockchain_service import BlockchainService
from django.conf import settings

class StockRequestViewSet(viewsets.ModelViewSet):
    queryset = StockRequest.objects.all()
    serializer_class = StockRequestSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        new_status = request.data.get('status')
        
        # Blockchain logging
        if new_status in ['APPROVED', 'REJECTED']:
            blockchain = BlockchainService()
            action = 1 if new_status == 'APPROVED' else 2  # Matches ActionType enum
            tx_hash = blockchain.log_action(
                item_id=instance.item.id,
                quantity=instance.quantity,
                action_type=action,
                private_key=settings.ADMIN_PRIVATE_KEY
            )
            instance.tx_hash = tx_hash
        
        instance.status = new_status
        instance.save()
        return Response({"status": "Updated", "tx_hash": tx_hash})


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

class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        try:
            blockchain = BlockchainService()
            tx_hash = blockchain.log_action(
                user=self.request.user,
                item_id=serializer.validated_data['item'].id,
                quantity=serializer.validated_data['quantity'],
                action_type=3  # STOCK_MOVEMENT
            )
            serializer.save(
                moved_by=self.request.user,
                tx_hash=tx_hash
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
class DamageReportViewSet(viewsets.ModelViewSet):
    queryset = DamageReport.objects.all()
    serializer_class = DamageReportSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            # Validate required fields
            required_fields = ['item', 'quantity', 'description', 'severity']
            if any(field not in request.data for field in required_fields):
                return Response(
                    {"error": f"Missing required fields: {', '.join(required_fields)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate quantity is positive
            if int(request.data['quantity']) <= 0:
                return Response(
                    {"error": "Quantity must be a positive number"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get the item and validate stock
            try:
                item = StockItem.objects.get(id=request.data['item'])
                if item.quantity < int(request.data['quantity']):
                    return Response(
                        {"error": "Damage quantity exceeds available stock"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except StockItem.DoesNotExist:
                return Response(
                    {"error": "Item not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Create the damage report
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            report = serializer.save(reporter=request.user)

            # Blockchain integration (optional - remove if not needed)
            if hasattr(self, 'blockchain_service'):
                try:
                    tx_hash = self.blockchain_service.log_action(
                        user=request.user,
                        item_id=item.id,
                        quantity=report.quantity,
                        action_type=4,  # DAMAGE_REPORT
                        severity=report.severity
                    )
                    report.tx_hash = tx_hash
                    report.save()
                except Exception as e:
                    # Log the error but don't fail the request
                    print(f"Blockchain error: {str(e)}")

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def get_queryset(self):
        """Filter to show only reports created by the current user"""
        return self.queryset.filter(reporter=self.request.user)
    
# inventory/views.py
class DepartmentRequestViewSet(viewsets.ModelViewSet):
    queryset = StockRequest.objects.all()
    serializer_class = DepartmentRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StockRequest.objects.filter(
            requester=self.request.user
        ).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        if request.user.user_type != 'DEPT_STAFF':
            return Response(
                {"error": "Only department staff can create requests"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Ensure item exists before proceeding
        item_id = request.data.get('item_id')
        if not item_id:
            return Response(
                {"error": "item_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            StockItem.objects.get(id=item_id)
        except StockItem.DoesNotExist:
            return Response(
                {"error": "Item does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Auto-set requester and department
        stock_request = serializer.save(
            requester=request.user,
            department=request.user.department,
            status='PENDING'
        )

        # Blockchain logging
        blockchain = BlockchainService()
        tx_hash = blockchain.log_action(
            item_id=stock_request.item.id,
            quantity=stock_request.quantity,
            action_type=0,  # REQUEST
            private_key=settings.DEPT_PRIVATE_KEY
        )
        stock_request.tx_hash = tx_hash
        stock_request.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class RequestStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            req = StockRequest.objects.get(pk=pk, requester=request.user)
            serializer = DepartmentRequestSerializer(req)
            return Response(serializer.data)
        except StockRequest.DoesNotExist:
            return Response(
                {"error": "Request not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
class SupplierDeliveryViewSet(viewsets.ModelViewSet):
    queryset = SupplierDelivery.objects.all()
    serializer_class = SupplierDeliverySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SupplierDelivery.objects.filter(supplier=self.request.user)

    def perform_create(self, serializer):
        if self.request.user.user_type != 'SUPPLIER':
            return Response(
                {"error": "Only suppliers can submit deliveries"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Create delivery
        delivery = serializer.save(supplier=self.request.user)

        # Blockchain logging
        try:
            blockchain = BlockchainService()
            tx_hash = blockchain.log_action(
                item_id=0,  # Using 0 for delivery records
                quantity=delivery.items.count(),
                action_type=5,  # DELIVERY_RECORD
                private_key=settings.SUPPLIER_PRIVATE_KEY
            )
            delivery.tx_hash = tx_hash
            delivery.save()
        except Exception as e:
            print(f"Blockchain error: {e}")

class DeliveryVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if request.user.user_type != 'MANAGER':
            return Response(
                {"error": "Only managers can verify"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        delivery = SupplierDelivery.objects.get(pk=pk)
        delivery.verified = True
        delivery.save()

        # Update stock quantities
        for item in delivery.deliveryitem_set.all():
            item.item.quantity += item.quantity
            item.item.save()

        return Response({"status": "Delivery verified"})