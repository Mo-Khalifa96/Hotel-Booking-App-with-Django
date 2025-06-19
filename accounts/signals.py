import logging 
from django.conf import settings
from django.dispatch import Signal
from django.dispatch import receiver
from accounts.utils import EmailThread
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.template.loader import render_to_string


#get user model 
User = get_user_model()

#Instantiate logger
logger = logging.getLogger(__name__)

#Custom function to get login url
def get_login_url(is_staff):
    protocol = settings.SITE_PROTOCOL 
    domain = settings.SITE_DOMAIN 
    path = '/staff/login/' if is_staff else '/guests/login/'
    return f"{protocol}://{domain}{path}"


#Registration welcome email (triggers automatically after saving)
@receiver(post_save, sender=User, dispatch_uid='welcome_email_handler')  
def welcome_email(sender, instance, created, **kwargs):
    if created: 
        login_url = get_login_url(instance.is_staff)
        html_message = render_to_string('emails/welcome_email.html', 
                        context={'user': instance,'login_url': login_url})
        plain_message = (f'Hi {instance.first_name} {instance.last_name}, thank you for registering with us!\n'
                         f'Please login here: {login_url}')
        
        EmailThread(
            subject='Welcome to Our Site!',
            message=plain_message,
            html_message=html_message,
            from_email = settings.DEFAULT_FROM_EMAIL,
            recipient_list = [instance.email],
            fail_silently=False
        ).start()


#Password Reset Successful Email
#create custom signal for confirming password reset 
password_reset_successful_signal = Signal()

#Successful password reset email
@receiver(password_reset_successful_signal)
def password_reset_successful_email(sender, is_staff, first_name, last_name, email, **kwargs):
    login_url = get_login_url(is_staff)
    html_message = render_to_string('emails/reset_successful_email.html', 
                    context={'first_name': first_name, 'last_name': last_name, 'login_url': login_url})
    
    plain_message = (f'Hi {first_name} {last_name},\n\nyour password has been reset successfully.\n'
                     f'You can now log in using your new credentials.\n'
                     f'Please login here: {login_url}\n\n'
                     f'If you did not perform this action, please contact our support team immediately.')

    EmailThread(
        subject='Password Reset Successfully',
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL, 
        recipient_list=[email],
        fail_silently=False
    ).start()


