import os
import sys
import re
import django
import random
from datetime import timedelta
from faker import Faker
from django.core.exceptions import ValidationError
from django.db import transaction
from pathlib import Path

#Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

#Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HotelBookingProject.settings.dev')
django.setup()

#import models 
from bookings.models import Branch, Room, Booking

#Instantiate faker
fake = Faker()



#Helper functions 
def clean_phone_number(raw_number):
    cleaned = re.sub(r'[^0-9\s\-\(\)\+]', '', raw_number)
    return cleaned.strip()[:20]

def get_price_for_room_type(room_type):
    price_ranges = {
        'single': (75, 120),
        'double': (140, 280),
        'deluxe': (125, 220),
        'double deluxe': (250, 400),
        'suite': (400, 700),
    }
    
    room_type_lower = room_type.strip().lower()
    if room_type_lower not in price_ranges:
        raise ValueError(f"Unknown room type: {room_type}")

    low, high = price_ranges[room_type_lower]
    return random.randrange(low, high + 1, 5) 


#Function to import branches from CSV
# @transaction.atomic
# def import_branches_data(csv_file_path):
#     with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             branch, created = Branch.objects.get_or_create(
#                 name=row['name'],
#                 defaults={
#                     'address': row['address'],
#                     'zipcode': row['zipcode'],
#                     'phone_number': row['phone_number'],
#                     'email': row['email'],
#                     'website': row.get('website') or None,
#                     'rating': row.get('rating') or None,
#                 }
#             )
#             if created:
#                 print(f'Imported Branch: {branch.name}')
#             else:
#                 print(f'Branch already exists: {branch.name}')


# #Function to import rooms from CSV
# @transaction.atomic
# def import_rooms_data(csv_file_path):
#     with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             try:
#                 branch = Branch.objects.get(name=row['branch_name'])
#                 room_type = row['room_type'].strip().lower()
#                 price = get_price_for_room_type(room_type)

#                 room, created = Room.objects.get_or_create(
#                     branch=branch,
#                     room_number=int(row['room_number']),
#                     room_type=room_type,
#                     defaults={
#                         'price_per_night': price,
#                         'is_available': row['is_available'].lower() == 'true'
#                     }
#                 )
#                 if created:
#                     print(f'Imported Room: {branch.name} - {room.room_number} (${price})')
#                 else:
#                     print(f'Room already exists: {branch.name} - {room.room_number}')
#             except Branch.DoesNotExist:
#                 print(f'Branch not found for room: {row["branch_name"]}')
#             except ValueError as e:
#                 print(f"Pricing error: {e}")


#Function to populate Booking model
@transaction.atomic
def populate_bookings(total_bookings):
    rooms = Room.objects.filter(is_available=True)
    if not rooms:
        print("No available rooms to create bookings.")
        return

    for _ in range(total_bookings):
        room = random.choice(rooms)
        
        #Extra safeguard to double-check availability
        if not room.is_available:
            continue

        branch = room.branch
        gender = random.choice(['male', 'female'])
        dob = fake.date_of_birth(minimum_age=18, maximum_age=70)
        check_in = fake.date_between(start_date='-10d', end_date='today')
        check_out = check_in + timedelta(days=random.randint(1, 7))

        #Generate raw phone number and clean it
        raw_phone = fake.unique.phone_number()
        phone_number = clean_phone_number(raw_phone)

        try:
            booking = Booking(
                guest_first_name=fake.first_name_male() if gender == 'male' else fake.first_name_female(),
                guest_last_name=fake.last_name(),
                date_of_birth=dob,
                gender=gender,
                nationality=fake.country(),
                phone_number=phone_number,
                email=fake.unique.email(),
                id_number=fake.unique.bothify(text='ID#######'),
                id_photo=None,
                branch=branch,
                room=room,
                check_in_date=check_in,
                check_out_date=check_out,
            )

            booking.full_clean()  #Run model validators before saving
            booking.save()

            room.is_available = False
            room.save()

            print('Bookings created successfully.')

        except ValidationError as e:
            print(f"Validation error while creating booking: {e}")

        except Exception as e:
            print(f"Skipping booking due to error: {e}")


#Run script
if __name__ == '__main__':
    print('Importing and populating data...')
    #import_branches_data('branches.csv')
    #import_rooms_data('rooms.csv')
    populate_bookings(50)
    print('Database successfully populated.')
