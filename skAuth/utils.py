import random
import string
from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import send_mail
from twilio.rest import Client

def generate_otp():
    return ''.join(random.choices(string.digits, k=4))

def send_email_otp(user, otp_code):
    subject = 'Your OTP for verification'
    message = f'Your OTP is: {otp_code}. This OTP will expire in 10 minutes.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    
    try:
        send_mail(subject, message, from_email, recipient_list)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def send_whatsapp_otp(user, otp_code):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    try:
        message = client.messages.create(
            body=f'Your OTP is: {otp_code}. This OTP will expire in 10 minutes.',
            from_=f'whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}',
            to=f'whatsapp:{user.phone_number}'
        )
        return True
    except Exception as e:
        print(f"Error sending WhatsApp message: {str(e)}")
        return False 