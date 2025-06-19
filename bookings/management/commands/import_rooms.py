import os 
import csv
from decimal import Decimal
from django.conf import settings 
from django.core.files import File 
from bookings.models import Room, Branch
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Import rooms from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('--csv-file', type=str, required=True)

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        media_root = settings.MEDIA_ROOT

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    branch = Branch.objects.get(id=row['branch_id'])
                    image_path = row.get('room_img', '').strip()
                    full_image_path = os.path.join(media_root, image_path) if image_path else None

                    #create room objects 
                    room, created = Room.objects.get_or_create(
                        branch=branch,
                        room_number=int(row['room_number']),
                        room_type=row['room_type'].lower().strip(),
                        defaults={
                            'price_per_night': Decimal(row['price_per_night']),
                            'is_available': row.get('is_available', 'true').lower() == 'true'
                        }
                    )
                    
                    if created:
                        # Attach image if file exists
                        if full_image_path and os.path.exists(full_image_path):
                            with open(full_image_path, 'rb') as img_file:
                                room.room_img.save(os.path.basename(image_path), File(img_file), save=True)
                        self.stdout.write(self.style.SUCCESS(f"Created room {room.room_number} in {branch.name}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"Room {room.room_number} already exists in {branch.name}"))

                except Branch.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Branch not found for room: {row}"))

                except Exception as exc:
                    self.stdout.write(self.style.ERROR(f"Error importing room: {row} - {exc}"))