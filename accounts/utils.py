import threading
import logging 
from django.conf import settings
from django.core.mail import send_mail

#Instantiate logger
logger = logging.getLogger(__name__)  

#Email sending class using threading 
class EmailThread(threading.Thread):
    def __init__(self, subject, message, from_email, recipient_list, html_message=None, fail_silently=False):
        self.subject = subject
        self.message = message
        self.from_email = from_email
        self.recipient_list = recipient_list 
        self.html_message = html_message
        self.fail_silently = fail_silently
        super().__init__()

    def run(self):
        try:
            mail_sent = send_mail(
                subject=self.subject,
                message=self.message,
                html_message=self.html_message,
                from_email=self.from_email,
                recipient_list=self.recipient_list,
                fail_silently=self.fail_silently)
        
            #log result        
            logger.info(f'Mail sent successfully: {mail_sent}')
        
        except Exception as exc:
            logger.warning(f'Failed to send email: {exc}')

