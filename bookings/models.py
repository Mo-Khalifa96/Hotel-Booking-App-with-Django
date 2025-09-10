from django.db import models
from django.db import transaction
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.validators import *


#Branch table to hotel branches
class Branch(models.Model):
    #Model Fields
    name = models.CharField(max_length=100, unique=True, blank=False, null=False)  
    address = models.CharField(max_length=250, unique=True, blank=False, null=False) 
    zipcode = models.CharField(max_length=10, unique=True, blank=False, null=False)  
    phone_number = models.CharField(max_length=20, unique=True) 
    email = models.EmailField(unique=True, blank=False, null=False)  
    website = models.URLField(blank=True, null=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    branch_slug = models.SlugField(unique=True, blank=True) 
    branch_img = models.ImageField(upload_to='branch_images/', blank=True, null=True)  

    class Meta:
        db_table = "Branches_table"  
        verbose_name_plural = 'Branches'
        ordering = ['name']  

    def __str__(self):
        return self.name   #the string stand-in for its value as a foreign key
    
     #Customize the save method 
    def save(self, *args, **kwargs):
        if not self.branch_slug:    #if the branch is new 
            #auto-generate the slug field based on hotel name 
            self.branch_slug = slugify(self.name)
        #save data 
        super().save(*args, **kwargs)  


#Rooms model to register info about branch rooms 
class Room(models.Model):
    ROOM_TYPES = [
        ('single', 'Single'), 
        ('double', 'Double'), 
        ('deluxe', 'Deluxe'), 
        ('double deluxe', 'Double Deluxe'), 
        ('suite', 'Suite')
    ]

    #Model Fields
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True)  
    room_number = models.IntegerField(unique=False)   
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES) 
    room_img = models.ImageField(upload_to='room_images/', blank=True, null=True)  
    price_per_night = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])
    is_available = models.BooleanField(default=True) 

    class Meta:
        db_table = 'Rooms_table'  
        verbose_name_plural = 'Rooms'  
        unique_together = ('branch', 'room_number', 'room_type')   
        ordering = ['branch', 'room_number']  
        
    def __str__(self):
        return f'{self.room_number}'   #the string stand-in for its value as a foreign key


#Guests manager class (for soft deleting guests)
class BookingsManager(models.Manager):
    #Overriding get_query to filter out soft-deleted records
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)  #filter out soft-deleted records

    #Custom method to soft-delete guest when invoked
    @transaction.atomic
    def delete_booking(self, booking_id):
        try:
            booking = self.get(id=booking_id)   #get booking by id 
            booking.room.is_available = True   #change room's availability
            booking.room.save()
            booking.is_deleted = True  # Soft delete
            booking.save()
            return True   
        
        except self.model.DoesNotExist:
            return False   
    
    @transaction.atomic
    def remove_canceled_booking(self, booking_id):
        try: 
            booking = self.get(id=booking_id)   #get booking by id 
            booking.room.is_available = True   #change room's availability
            booking.room.save()
            booking.delete()  #remove completely
            return True 
        except self.model.DoesNotExist:
            return False 

#Guests model to register hotel guests 
class Booking(models.Model):
    #Model Fields 
    #Guest-related fields 
    guest_first_name = models.CharField(max_length=120)
    guest_last_name = models.CharField(max_length=120)
    date_of_birth = models.DateField(blank=False, null=True, validators=[validate_age])
    gender = models.CharField(max_length=10, choices=(('male', 'Male'), ('female', 'Female')))
    nationality = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20, unique=True, validators=[validate_phone_number])
    email = models.EmailField(blank=True, null=True, unique=True)
    id_number = models.CharField(max_length=40, unique=True, blank=False, null=True)
    id_photo = models.ImageField (upload_to='id_photos/', blank=True, null=True, validators=[validate_image_size])  
    
    #Hotel-related fields 
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE) 
    room = models.ForeignKey(Room, null=True, on_delete=models.CASCADE) 
    check_in_date = models.DateField(verbose_name='Check-in date')
    check_out_date = models.DateField(verbose_name='Check-out date')
    booking_date = models.DateTimeField(auto_now_add=True) 
    last_modified = models.DateTimeField(auto_now=True)
    check_in_reminder_sent = models.BooleanField(default=False)  #Reminder email flag
    is_deleted = models.BooleanField(default=False)  #Soft delete field

    #Objects after filtering by manager
    objects = BookingsManager()  

    #to access all objects
    all_objects = models.Manager()


    class Meta:
        db_table = 'Bookings_table'
        verbose_name_plural = 'Bookings'
        unique_together = ('guest_first_name', 'guest_last_name', 'branch', 'room', 'check_in_date')

    def __str__(self):
        return f'{self.guest_first_name} {self.guest_last_name}'
    

    def clean(self):        
        #Check if selected room is available
        if self.room:   #if the room exists 
            #if this is a new guest
            if not self.pk:  
                if not self.room.is_available:    
                    raise ValidationError({'room': 'The selected room is already booked or unavailable'})            
            
            else:  
                #else, if existing guest, fetch original booking object
                guest_data = Booking.all_objects.get(pk=self.pk)  
                #check if the room has changed
                if self.room.room_number != guest_data.room.room_number: 
                    #check if the new room is available
                    if not self.room.is_available:   
                        raise ValidationError({'room': 'The selected room is already booked or unavailable'})
        super().clean()
    

