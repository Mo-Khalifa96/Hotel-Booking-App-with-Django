import os 
import csv
from decimal import Decimal
from django.conf import settings 
from django.core.files import File
from bookings.models import Branch
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Import branches from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('--csv-file', type=str, required=True)

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        media_root = settings.MEDIA_ROOT

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    image_path = row.get('branch_img', '').strip()
                    branch_img_path = os.path.join(media_root, image_path) if image_path else None

                    #create branch objects 
                    branch, created = Branch.objects.get_or_create(
                        name=row['name'],
                        defaults={
                            'address': row['address'],
                            'zipcode': row['zipcode'],
                            'phone_number': row['phone_number'],
                            'email': row['email'],
                            'website': row.get('website') or None,
                            'rating': Decimal(row.get('rating')) or None
                        }
                    )
                    
                    if created:
                        #assign branch image 
                        if branch_img_path and os.path.exists(branch_img_path):
                            with open(branch_img_path, 'rb') as img_file:
                                branch.branch_img.save(os.path.basename(image_path), File(img_file), save=True)
                        self.stdout.write(self.style.SUCCESS(f"Created branch: {branch.name}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"Branch already exists: {branch.name}"))

                except Exception as exc:
                    self.stdout.write(self.style.ERROR(f"Error importing branch: {row['name']} - {exc}"))