from django.shortcuts import render
from .models import User, OTP
from .utils import generate_otp, send_email_otp, send_whatsapp_otp
from datetime import datetime, timedelta
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer, RegisterSerializer, CustomTokenObtainPairSerializer
)

User = get_user_model()

# Create your views here.

def create_and_send_otp(user, otp_type):
    otp_code = generate_otp()
    expires_at = datetime.now() + timedelta(minutes=10)
    
    otp = OTP.objects.create(
        user=user,
        otp_type=otp_type,
        otp_code=otp_code,
        expires_at=expires_at
    )
    
    if otp_type == 'email':
        send_email_otp(user, otp_code)
    else:
        send_whatsapp_otp(user, otp_code)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        # Send verification OTP
        create_and_send_otp(user, 'email')
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class VerifyOTPView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        otp_code = request.data.get('otp_code')
        otp_type = request.data.get('otp_type', 'email')

        try:
            otp = OTP.objects.get(
                user=request.user,
                otp_type=otp_type,
                otp_code=otp_code,
                is_verified=False,
                expires_at__gt=datetime.now()
            )
            otp.is_verified = True
            otp.save()

            if otp_type == 'email':
                request.user.verified_status = 'verified'
                request.user.save()

            return Response({'message': 'OTP verified successfully'})
        except OTP.DoesNotExist:
            return Response(
                {'error': 'Invalid or expired OTP'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
