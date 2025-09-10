import re 
import random
import datetime
from django.db import models  
from django.contrib.auth.models import AbstractUser, BaseUserManager
from accounts.validators import validate_age, validate_image_size, validate_phone_number


#User manager 
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **kwargs):
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)

        #other defaults (handled when not required during creation)
        kwargs.setdefault("gender", "male")
        kwargs.setdefault("date_of_birth", datetime.date.today())
        kwargs.setdefault("phone_number", self.make_random_phone_number())

        return self.create_user(email, password, **kwargs)

    def make_random_phone_number(self):
        return f"0000{random.randint(100000, 999999)}" 

#Define custom User class 
class User(AbstractUser):
    first_name = models.CharField(max_length=50, blank=False, null=False)
    last_name = models.CharField(max_length=50, blank=False, null=False)
    username = models.CharField(max_length=50, unique=False, blank=True, null=True) 
    date_of_birth = models.DateField(blank=False, null=False, validators=[validate_age])
    gender = models.CharField(max_length=10, choices=(('male', 'Male'), ('female', 'Female')))
    nationality = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=120, unique=True, blank=False, null=False)
    phone_number = models.CharField(max_length=20, blank=False, null=False, unique=True, validators=[validate_phone_number])
    profile_picture = models.ImageField(upload_to='profile_pics/', validators=[validate_image_size], blank=True, null=True)
    id_number = models.CharField(max_length=50, blank=True, null=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(auto_now=True)
    date_joined = models.DateTimeField(auto_now_add=True)


    USERNAME_FIELD = 'email'

    #fields for superusers 
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username'] 

    objects = UserManager()

    all_objects = models.Manager()    

    class Meta: 
        db_table = 'User_table'
        verbose_name_plural = 'Users'
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    #Custom static function to normalize phone numbers 
    @staticmethod
    def normalize_phone_number(phone_number):
        phone_number_normalized = phone_number.replace('+', '00', 1) if phone_number.startswith('+') else phone_number
        return re.sub(r'[^\d]', '', phone_number_normalized) 


#Set up different profiles for guests, staff, and management 
class Guest(models.Model):
    guest = models.OneToOneField(User, on_delete=models.CASCADE)
    is_subscribed = models.BooleanField(default=True)

    class Meta:
        db_table = 'Guests_table'
        verbose_name_plural = 'Guests'
        ordering = ['guest__first_name', 'guest__last_name']


class Staff(models.Model):
    member = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20)
    branch = models.ForeignKey('bookings.Branch', on_delete=models.SET_NULL, blank=True, null=True)
    shift_time = models.CharField(max_length=20, choices=(('morning', 'Morning Shift'), ('night', 'Night Shift')))

    class Meta:
        db_table = 'Staff_table'
        verbose_name_plural = 'Staff'
        ordering = ['member__first_name', 'member__last_name']


class Management(models.Model):
    manager = models.OneToOneField(User, on_delete=models.CASCADE)
    management_level = models.CharField(max_length=35, blank=False, null=False)
    branch = models.ForeignKey('bookings.Branch', on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = 'Management_table'
        verbose_name_plural = 'Management'
        ordering = ['manager__first_name', 'manager__last_name']
    
