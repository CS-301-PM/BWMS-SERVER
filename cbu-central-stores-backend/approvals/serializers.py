from rest_framework import serializers
from .models import Approval
from authentication.serializers import UserSerializer  # To nest approver details

class ApprovalSerializer(serializers.ModelSerializer):
    """Serializer for the Approval model."""
    # Read-only fields to provide more detail in the API response
    approver_name = serializers.CharField(source='approver.get_full_name', read_only=True)
    stage_display = serializers.CharField(source='get_stage_display', read_only=True)
    request_id = serializers.IntegerField(source='request.id', read_only=True)

    class Meta:
        model = Approval
        fields = '__all__'
        read_only_fields = ('id', 'date_created', 'date_updated', 'approver')

class ApprovalStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for an approver to update the status of their assigned stage."""
    class Meta:
        model = Approval
        fields = ('status', 'comment')  # Only these fields can be updated via this serializer