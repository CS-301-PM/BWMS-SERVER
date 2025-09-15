from rest_framework import serializers
from .models import BlockchainLog

class BlockchainLogSerializer(serializers.ModelSerializer):
    """Serializer for the BlockchainLog model."""
    class Meta:
        model = BlockchainLog
        fields = '__all__'
        read_only_fields = ('id', 'date_logged', 'logged_by')