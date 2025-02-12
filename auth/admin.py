from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, OTP

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'verified_status', 'is_staff')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('verified_status', 'is_staff', 'is_superuser')

class OTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp_type', 'created_at', 'expires_at', 'is_verified')
    search_fields = ('user__email', 'user__username')
    list_filter = ('otp_type', 'is_verified')

admin.site.register(User, CustomUserAdmin)
admin.site.register(OTP, OTPAdmin)
