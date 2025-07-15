from rest_framework import serializers
from .models import StockItem, StockRequest

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