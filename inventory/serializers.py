from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    """Serializer for the Product model. Includes computed low_stock status."""
    is_low_stock = serializers.BooleanField(read_only=True) # Make the property available in API

    class Meta:
        model = Product
        fields = '__all__' # Include all model fields
        read_only_fields = ('id', 'date_created', 'date_updated') # These are auto-set