import random
import string
from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import EmailMessage
from twilio.rest import Client

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_email_otp(user, otp_code):
    try:
        subject = 'Your ShotterKotha Verification Code'
        message = f"""
        Hi {user.first_name},

        Your verification code is: {otp_code}

        This code will expire in 10 minutes.

        If you didn't request this code, please ignore this email.

        Best regards,
        ShotterKotha Team
        """
        
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
            reply_to=[settings.DEFAULT_FROM_EMAIL]
        )
        
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def send_whatsapp_otp(user, otp_code):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    try:
        message = client.messages.create(
            body=f'Your ShotterKotha verification code is: {otp_code}. This code will expire in 10 minutes.',
            from_=f'whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}',
            to=f'whatsapp:{user.phone_number}'
        )
        return True
    except Exception as e:
        print(f"Error sending WhatsApp message: {str(e)}")
        return False 