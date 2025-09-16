# utils/api_views.py
from django.db.models import F  # Import F object directly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from inventory.models import Product
from procurement_requests.models import DepartmentRequest
from approvals.models import Approval
from authentication.models import User

class DashboardView(APIView):
    """API endpoint to get summary data for the dashboard."""
    permission_classes = [IsAuthenticated]

    
    def get(self, request):
        user = request.user
        
        # Base data available to all authenticated users
        data = {
            'total_products': Product.objects.count(),
            'low_stock_products': Product.objects.filter(quantity__lte=F('low_stock_threshold')).count(),
            'pending_requests': DepartmentRequest.objects.filter(status='PENDING').count(),
        }

        # Role-specific data
        if user.role in [User.Role.STORES_MANAGER, User.Role.ADMIN]:
            data['total_requests'] = DepartmentRequest.objects.count()
            data['approved_requests'] = DepartmentRequest.objects.filter(status='APPROVED').count()

        if user.role in [User.Role.STORES_MANAGER, User.Role.PROCUREMENT_OFFICER, User.Role.CFO, User.Role.ADMIN]:
            # Show each user their pending approvals
            role_stage_map = {
                User.Role.STORES_MANAGER: Approval.Stage.STORES,
                User.Role.PROCUREMENT_OFFICER: Approval.Stage.PROCUREMENT,
                User.Role.CFO: Approval.Stage.CFO,
            }
            if user.role in role_stage_map:
                user_stage = role_stage_map[user.role]
                data['my_pending_approvals'] = Approval.objects.filter(
                    stage=user_stage, 
                    approver=user,
                    status='PENDING'
                ).count()

        return Response(data)