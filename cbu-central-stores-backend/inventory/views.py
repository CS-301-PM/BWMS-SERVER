from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action

from authentication import models

from .models import Product
from .serializers import ProductSerializer
from .permissions import IsStoresManagerOrAdmin
from rest_framework.permissions import IsAuthenticated 
from authentication.models import User
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

@extend_schema_view(
    list=extend_schema(description="List all products with optional filtering"),
    retrieve=extend_schema(description="Retrieve a specific product by ID"),
    create=extend_schema(description="Create a new product (Stores Manager only)"),
    update=extend_schema(description="Update a product (Stores Manager only)"),
    partial_update=extend_schema(description="Partial update of a product"),
    destroy=extend_schema(description="Delete a product (Stores Manager only)"),
    adjust_stock=extend_schema(
        description="Adjust product stock quantity",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'adjustment': {'type': 'integer', 'description': 'Quantity to adjust (can be negative)'}
                }
            }
        }
    ),
    low_stock=extend_schema(description="List products with low stock levels")
)
class ProductViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and managing products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsStoresManagerOrAdmin]

    def get_queryset(self):
        """Optionally filter by category or low stock status"""
        queryset = Product.objects.all()
        category = self.request.query_params.get('category')
        low_stock = self.request.query_params.get('low_stock')

        if category:
            queryset = queryset.filter(category=category)
        if low_stock and low_stock.lower() == 'true':
            queryset = queryset.filter(quantity__lte=models.F('low_stock_threshold'))

        return queryset

    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        """Custom API action to increase or decrease stock."""
        product = self.get_object()
        try:
            adjustment = int(request.data.get('adjustment', 0))
        except (TypeError, ValueError):
            return Response({'error': 'Adjustment must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent stock from going negative
        if (product.quantity + adjustment) < 0:
            return Response({'error': 'Insufficient stock.'}, status=status.HTTP_400_BAD_REQUEST)

        product.quantity += adjustment
        product.save()

        serializer = self.get_serializer(product)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Custom endpoint to list all products that are low on stock."""
        low_stock_products = Product.objects.filter(quantity__lte=models.F('low_stock_threshold'))
        page = self.paginate_queryset(low_stock_products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(low_stock_products, many=True)
        return Response(serializer.data)
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def low_stock_alerts(self, request):
        """
        Custom endpoint to get detailed list of low stock products.
        Only accessible to Stores Manager, Procurement, CFO, and Admin.
        """
        from authentication.models import User
        user = request.user
        
        # Permission check: Only relevant roles can see low stock alerts
        if user.role not in [User.Role.STORES_MANAGER, User.Role.PROCUREMENT_OFFICER, User.Role.CFO, User.Role.ADMIN]:
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        low_stock_products = Product.objects.filter(quantity__lte=models.F('low_stock_threshold'))
        serializer = self.get_serializer(low_stock_products, many=True)
        return Response(serializer.data)