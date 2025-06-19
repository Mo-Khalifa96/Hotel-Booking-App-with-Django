import logging
from django.apps import AppConfig

#Instantiate logger
logger = logging.getLogger(__name__)

class BookingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bookings'

    def ready(self):
        try:
            import bookings.signals
            logger.info("Bookings signals loaded successfully.")
        except Exception as exc:
            logger.error('Failed to import signals in BookingsConfig ready().')
            logger.exception(exc)
