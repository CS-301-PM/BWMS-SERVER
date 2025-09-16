from rest_framework import serializers

class ApprovalActionSerializer(serializers.Serializer):
    """
    Serializer for validating the input to the ApprovalActionView.
    """
    action = serializers.ChoiceField(choices=['APPROVE', 'REJECT', 'SUGGEST_RESUBMISSION'])
    comments = serializers.CharField(required=False, allow_blank=True)