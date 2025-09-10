import logging 
from django.dispatch import receiver
from django.conf import settings
from django.dispatch import Signal
from accounts.utils import EmailThread
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.template.loader import render_to_string
from bookings.models import Booking

#get user model 
User = get_user_model()

#Instantiate logger
logger = logging.getLogger(__name__)


#Custom function to get booking detail url
def get_booking_detail_url(booking_id):
    protocol = settings.SITE_PROTOCOL 
    domain = settings.SITE_DOMAIN 
    path = f'/guests/bookings/{booking_id}'
    return f'{protocol}://{domain}{path}'



#Booking confirmation email signal
@receiver(post_save, sender=Booking, dispatch_uid='booking_confirmation_email_handler')  
def booking_confirmation_email(sender, instance, created, **kwargs):
    if created: 
        booking_detail_url = get_booking_detail_url(instance.id)
        html_message = render_to_string('emails/booking_confirmation_email.html', 
                        context={'booking': instance, 'booking_detail_url': booking_detail_url})
        plain_message = (f'Hi {instance.guest_first_name} {instance.guest_last_name}, thank you for booking with us!\n'
                         f'You can view or change your booking details here: {booking_detail_url}')
        
        EmailThread(
            subject='Your room was booked successfully',
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            fail_silently=False
        ).start()



#Booking changed email signal 
#create custom signal 
booking_updated_signal = Signal()

#booking change signal
@receiver(booking_updated_signal, dispatch_uid='booking_updated_email_handler')
def booking_updated_email(sender, booking, **kwargs):
    #html template with the booking
    html_message = render_to_string('emails/booking_update_confirmation.html', context={'booking': booking})
    #plain message
    plain_message = (
        f'Hi {booking.guest_first_name} {booking.guest_last_name},\n\n'
        f'Your booking has been updated successfully.\n\n'
        f'Current booking details:\n'
        f'Guest name: {booking.guest_first_name} {booking.guest_last_name}\n'
        f'Phone number: {booking.phone_number}\n' 
        f'Branch: {booking.branch.name}\n'
        f'Room: {booking.room.room_number}\n'
        f'Check-in date: {booking.check_in_date}\n'
        f'Check-out date: {booking.check_out_date}'
    )

    EmailThread(
        subject='Your booking has been updated',
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[booking.email],
        fail_silently=False
    ).start()


#Room changed email signal 
#create room change signal
room_changed_signal = Signal()

@receiver(room_changed_signal, dispatch_uid='room_changed_email_handler')
def room_changed_email(sender, booking, old_room, **kwargs):
    html_message = render_to_string('emails/room_change_confirmation.html', 
                    context={'booking': booking, 'old_room': old_room})

    plain_message = (
        f'Hi {booking.guest_first_name} {booking.guest_last_name},\n\n'
        f'Your room has been successfully changed from Room {old_room.room_number} to Room {booking.room.room_number}.'
    )

    EmailThread(
        subject='Your room has been changed',
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[booking.email],
        fail_silently=False
    ).start()


#Booking canceled email signal 
@receiver(post_delete, sender=Booking, dispatch_uid='booking_cancelled_email_handler')
def booking_cancellation_email(sender, instance, **kwargs):
    html_message = render_to_string('emails/booking_cancelled_email.html', context={'booking': instance})
    
    plain_message = (f"Hi {instance.guest_first_name} {instance.guest_last_name},\n\n"
                     f"Your booking has been cancelled successfully. If this was a mistake, please contact our support team immediately.\n")
    
    EmailThread(
        subject='Your booking has been cancelled',
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[instance.email],
        fail_silently=False
    ).start()

