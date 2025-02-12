from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class User(AbstractUser):
    VERIFICATION_STATUS = (
        ('unverified', 'Unverified'),
        ('pending', 'Pending'),
        ('verified', 'Verified')
    )
    
    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    verified_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS,
        default='unverified'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

class OTP(models.Model):
    OTP_TYPE = (
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp')
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_type = models.CharField(max_length=10, choices=OTP_TYPE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = "OTP"
        verbose_name_plural = "OTPs"
