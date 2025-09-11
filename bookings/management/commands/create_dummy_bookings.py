from seed.SeedData import populate_bookings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create 50 dummy bookings to test the system.'

    def handle(self, *args, **kwargs):
        populate_bookings(50)

