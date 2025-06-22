import logging
from django.conf import settings
from celery import shared_task
from django.utils import timezone
from bookings.models import Booking
from accounts.utils import EmailThread
from datetime import date, timedelta
from django.template.loader import render_to_string

#Instantiate logger 
logger = logging.getLogger(__name__) 

#Custom function to get booking detail url
def get_booking_detail_url(booking_id):
    protocol = settings.SITE_PROTOCOL 
    domain = settings.SITE_DOMAIN 
    path = f'/guests/bookings/{booking_id}'
    return f'{protocol}://{domain}{path}'


#Clean up expired bookings (set is_deleted to False)
@shared_task(bind=True)
def cleanup_expired_bookings_task(self):
    try:
        today = date.today()
        expired_bookings = Booking.objects.filter(check_out_date__lt=today)
        expired_bookings.update(is_deleted=True)
    except Exception as exc:
        logger.error(f'\nCleaning up expired bookings task failed:\n{exc}.\n\nTrying again...')
        self.retry(exc=exc, countdown=60, max_retries=10, retry_backoff=True, retry_backoff_max=60*5)


#Reminder email one day before check-in task
@shared_task(bind=True)
def check_in_reminder_email_task(self):
    try:
        date_now = timezone.now()
        window_start = date_now + timedelta(hours=24)
        window_end = date_now + timedelta(hours=28) 

        bookings = Booking.objects.filter(check_in_date__gte=window_start, 
                                          check_in_date__lt=window_end, 
                                          check_in_reminder_sent=False)

        for booking in bookings:
            booking_detail_url = get_booking_detail_url(booking.id)
            html_message = render_to_string('emails/check_in_reminder_email.html', 
                            context={'booking': booking, 'booking_detail_url': booking_detail_url})

            plain_message = (
                f"Hi {booking.guest_first_name} {booking.guest_last_name},\n\n"
                f"This is a friendly reminder that your stay at Khalifa Hotels is scheduled to begin in less than 24 hours.\n\n"
                f"Here are your booking details:\n"
                f"Guest Name: {booking.guest_first_name} {booking.guest_last_name}\n"
                f"Phone Number: {booking.phone_number}\n"
                f"Email: {booking.email}\n"
                f"Branch: {booking.branch.name}\n"
                f"Room Number: {booking.room.room_number}\n"
                f"Check-in Date: {booking.check_in_date}\n"
                f"Check-out Date: {booking.check_out_date}\n\n"
                f"Please double-check your check-in date and let us know if you need to make any changes.\n\n"
                f"You can view your booking here: {booking_detail_url}\n\n"
                f"If you have any questions or need assistance, feel free to contact our support team.\n\n"
                f"Warm regards,\n"
                f"Khalifa Hotels"
            )

            EmailThread(
                subject='Upcoming Check-In Reminder - Khalifa Hotels',
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.email],
                fail_silently=False
            ).start()

            #mark check-in reminder as sent
            booking.check_in_reminder_sent = True
            booking.save(update_fields=['check_in_reminder_sent'])

        logger.info(f"Check-in reminder task completed successfully. {bookings.count()} emails sent.")
    
    except Exception as exc:
        logger.error(f'\nCheck-in reminder email task failed:\n{exc}.\n\nTrying again...')
        self.retry(exc=exc, countdown=30, max_retries=10, retry_backoff=True, retry_backoff_max=60*10)


