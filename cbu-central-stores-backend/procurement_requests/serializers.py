from rest_framework import serializers
from .models import DepartmentRequest
from inventory.serializers import ProductSerializer  # To nest product details

class DepartmentRequestSerializer(serializers.ModelSerializer):
    """Serializer for the DepartmentRequest model."""

    # These read-only fields provide more detail in the API response
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    product_detail = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = DepartmentRequest
        fields = '__all__'
        read_only_fields = ('id', 'requested_by', 'status', 'stores_comment', 'date_requested', 'date_updated')

class DepartmentRequestStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer specifically for Stores Manager to update the status and add a comment."""
    class Meta:
        model = DepartmentRequest
        fields = ('status', 'stores_comment')