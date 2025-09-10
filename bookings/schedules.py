from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from django.conf import settings

def clean_up_expired_bookings_schedule():
    crontab_schedule, _ = CrontabSchedule.objects.get_or_create(
        hour='0', minute='0')  #runs at midnight

    #Create the periodic task with the defined schedule
    task, created = PeriodicTask.objects.get_or_create(
        crontab=crontab_schedule,
        name='Clean up expired bookings',
        task='bookings.tasks.cleanup_expired_bookings_task'
    )

    if created:
        task.enabled = True
        task.save()

def check_in_reminder_schedule():
    interval_schedule, _ = IntervalSchedule.objects.get_or_create(
        period='hours', every=4)  #runs every 4 hours

    #Create the periodic task with the defined schedule
    task, created = PeriodicTask.objects.get_or_create(
        interval=interval_schedule,
        name='Send reminder email to guests with upcoming booking',
        task='bookings.tasks.check_in_reminder_email_task'
    )

    if created:
        task.enabled = True
        task.save()
