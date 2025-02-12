from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 
            'phone_number', 'verified_status', 'address', 'district',
            'division', 'fullAddress', 'longitude', 'latitude'
        )
        read_only_fields = ('verified_status',)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'email', 'username', 'password', 'password2', 
            'first_name', 'last_name', 'phone_number',
            'address', 'district', 'division', 'fullAddress',
            'longitude', 'latitude'
        )
        extra_kwargs = {
            'address': {'required': False},
            'district': {'required': False},
            'division': {'required': False},
            'fullAddress': {'required': False},
            'longitude': {'required': False},
            'latitude': {'required': False},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data

class UserLocationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user location details only"""
    class Meta:
        model = User
        fields = ('address', 'district', 'division', 'fullAddress', 'longitude', 'latitude') 