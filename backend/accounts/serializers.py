from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for returning safe user information.
    Does not expose password or sensitive internal fields.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone', 'role', 'is_verified', 'is_active')
        read_only_fields = fields

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for public user registration.
    """
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    
    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'phone', 'role')

    def validate_phone(self, value):
        """
        Validate that the phone number is reasonable and non-empty.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Phone number cannot be empty.")
        
        # Simple heuristic: at least 5 characters and contains digits
        if len(value) < 5 or not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Please provide a valid phone number.")
        return value

    def create(self, validated_data):
        # We always create normal users as USER role, regardless of what they might send in 'role'
        validated_data.pop('role', None)
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data.get('phone', ''),
            role=User.Role.USER
        )
        return user
