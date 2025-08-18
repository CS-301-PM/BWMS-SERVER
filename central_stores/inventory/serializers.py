from rest_framework import serializers
from .models import DamageReport, DeliveryItem, StockItem, StockMovement, StockRequest, SupplierDelivery

class StockItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockItem
        fields = '__all__'

class StockRequestSerializer(serializers.ModelSerializer):
    item = StockItemSerializer(read_only=True)
    requester = serializers.StringRelatedField()
    
    class Meta:
        model = StockRequest
        fields = '__all__'
        read_only_fields = ('tx_hash', 'created_at')

# inventory/serializers.py
class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = '__all__'
        read_only_fields = ('moved_by', 'from_location', 'tx_hash')

class DamageReportSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = DamageReport
        fields = ['id', 'item', 'quantity', 'description', 'severity', 'resolved', 'created_at']
        read_only_fields = ['id', 'resolved', 'created_at']
        extra_kwargs = {
            'quantity': {'required': True},
            'description': {'required': True},
            'severity': {'required': True}
        }

class DepartmentRequestSerializer(serializers.ModelSerializer):
    item = StockItemSerializer(read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=StockItem.objects.all(),
        source='item',
        write_only=True
    )
    
    class Meta:
        model = StockRequest
        fields = [
            'id', 'item', 'item_id', 'quantity', 'status', 
            'created_at', 'department', 'urgent', 'tx_hash'
        ]
        read_only_fields = [
            'status', 'created_at', 'department', 
            'requester', 'tx_hash'
        ]

class DeliveryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryItem
        fields = ['item', 'quantity']

class SupplierDeliverySerializer(serializers.ModelSerializer):
    items = DeliveryItemSerializer(many=True)
    
    class Meta:
        model = SupplierDelivery
        fields = '__all__'
        read_only_fields = ('supplier', 'tx_hash', 'verified')