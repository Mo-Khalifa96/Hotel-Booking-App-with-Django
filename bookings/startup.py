import logging
import threading

logger = logging.getLogger(__name__) 

already_executed = threading.Event()

def run_startup_tasks():
    if not already_executed.is_set():
        from bookings.schedules import (
            clean_up_expired_bookings_schedule,
            check_in_reminder_schedule
        )

        try:
            clean_up_expired_bookings_schedule()
        except Exception as exc:
            logger.error('\nBookings clean up task failed to execute...')
            logger.exception(exc)

        try:
            check_in_reminder_schedule()
        except Exception as exc:
            logger.error('\nCheck-in reminder schedule failed to execute...')
            logger.exception(exc)

        already_executed.set()
