from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializes registration requests and creates a new user."""
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'role', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Use the create_user method to handle password hashing
        return User.objects.create_user(**validated_data)

class UserLoginSerializer(serializers.Serializer):
    """Serializes login requests."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials. Please try again.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
        else:
            raise serializers.ValidationError('Must include "username" and "password".')

        data['user'] = user
        return data

class UserSerializer(serializers.ModelSerializer):
    """Serializes User model for general output (e.g., profile viewing)."""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'first_name', 'last_name', 'is_staff')
        read_only_fields = ('id', 'is_staff')  # These should not be changed via this serializer