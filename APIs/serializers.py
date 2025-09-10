import re 
from rest_framework import serializers
from datetime import datetime, timedelta
from django.contrib.auth import authenticate
from accounts.models import User, Guest 
from bookings.models import Booking, Branch, Room 
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q 

#Accepted date formats
DATE_INPUT_FORMATS = ['%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y', '%d.%m.%Y', '%Y/%m/%d', 'iso-8601']

#Account Management Serializers 
#Custom JWT authentication serializer 
class CreateTokenSerializer(TokenObtainPairSerializer):  #used for logins
    email_or_phone = serializers.CharField(label='Email or phone')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop(self.username_field,None)

    def validate(self, data):
        email_or_phone = data.get('email_or_phone')
        password = data.get('password')

        #validate email or phone number
        if '@' in email_or_phone:
            if not User.objects.filter(email__iexact=email_or_phone):
                raise serializers.ValidationError('No account with the email provided.')
        else:
            #normalize phone number 
            email_or_phone = User.normalize_phone_number(email_or_phone)
            if not User.objects.filter(phone_number=email_or_phone).exists():
                raise serializers.ValidationError('No account with the phone number provided.')

        user = authenticate(request=self.context.get('request'), username=email_or_phone, password=password)
        if not user:
            raise serializers.ValidationError('Invalid login credentials.')
        
        #Generate and return tokens 
        refresh = RefreshToken.for_user(user)
        return {'refresh': str(refresh), 'access': str(refresh.access_token)}


#Staff Registeration Serializer 
class StaffRegistrationSerializer(serializers.ModelSerializer):
    role = serializers.CharField(max_length=20)
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    shift_time = serializers.ChoiceField(choices=[('morning', 'Morning Shift'), ('night', 'Night Shift')])
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'gender', 
                  'date_of_birth', 'id_number', 'profile_picture', 'branch', 
                  'role', 'shift_time', 'password1', 'password2']

    #validate data 
    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError('Passwords do not match.')
        return data

#Guest Registeration Serializer 
class GuestRegistrationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    is_subscribed = serializers.BooleanField(default=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'gender', 'date_of_birth',
                  'nationality', 'id_number', 'profile_picture', 'password1', 'password2', 'is_subscribed']


    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError('Passwords do not match.')
        return data


#Bookings Management Serializers 
#Create Booking Serializer 
class CreateBookingSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)  #passed via view
    date_of_birth = serializers.DateField(input_formats=['%Y-%m-%d', '%d-%m-%Y'])
    check_in_date = serializers.DateField(input_formats=['%Y-%m-%d', '%d-%m-%Y'])
    check_out_date = serializers.DateField(input_formats=['%Y-%m-%d', '%d-%m-%Y'])

    class Meta:
        model = Booking
        fields = ['branch_name', 'guest_first_name', 'guest_last_name', 'gender', 'date_of_birth', 'nationality',
                'phone_number', 'email', 'id_number', 'id_photo',  'room', 'check_in_date', 'check_out_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        branch = self.context.get('branch')  #branch object passed from view (CreateBookingAPIView)
        
        if branch:
            self.branch = branch
            self.fields['branch_name'].default = branch.name
            self.fields['room'].queryset = Room.objects.select_related('branch').filter(branch=branch, is_available=True)


    def validate_room(self, room):
        if room and not room.is_available:
            raise serializers.ValidationError('This room is already booked!')
        return room
  

#Request Booking Serializer 
class RequestBookingSerializer(serializers.ModelSerializer):
    email_or_phone = serializers.CharField(max_length=50, required=True, label='Email or Phone Number')

    class Meta: 
        model = Booking 
        fields = ['guest_first_name', 'guest_last_name', 'email_or_phone']
    
    def validate(self, data):
        guest_first_name = data.get('guest_first_name')
        guest_last_name = data.get('guest_last_name')
        guest_email_or_phone = data.get('email_or_phone')

        #make sure all data are provided
        if not (guest_first_name and guest_last_name and guest_email_or_phone):
            return data 
        
        #validate name 
        if not Booking.objects.filter(guest_first_name__iexact=guest_first_name, guest_last_name__iexact=guest_last_name):
            raise serializers.ValidationError('No booking with the name provided.')
        
        #validate email or phone number
        if '@' in guest_email_or_phone:
            if not Booking.objects.filter(email__iexact=guest_email_or_phone):
                raise serializers.ValidationError('No booking with the email address provided.')
        else:
            guest_email_or_phone = User.normalize_phone_number(guest_email_or_phone)
            if not Booking.objects.filter(phone_number=guest_email_or_phone).exists():
                raise serializers.ValidationError('No booking with the phone number provided.')

        #get requested booking and pass it to cleaned data
        requested_booking = Booking.objects.filter(
            (Q(guest_first_name=guest_first_name) & Q(guest_last_name=guest_last_name)) & 
            (Q(email=guest_email_or_phone) | Q(phone_number=guest_email_or_phone))   
        ).first()

        #validate that booking exists
        if not requested_booking:
            raise serializers.ValidationError('No booking found with the provided details.')

        #add the booking to data 
        data['requested_booking'] = requested_booking
        return data

#Change Booking Serializer 
class ChangeBookingSerializer(serializers.ModelSerializer):
    old_branch = serializers.CharField(read_only=True, label='Current Branch')
    new_branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.none())
    old_room = serializers.CharField(read_only=True)
    new_room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.none())
    new_check_in_date = serializers.DateField()
    new_check_out_date = serializers.DateField()

    class Meta:
        model = Booking
        fields = ['guest_first_name', 'guest_last_name', 'phone_number', 'old_branch', 'new_branch', 
                'old_room', 'new_room', 'new_check_in_date', 'new_check_out_date']

    def __init__(self, *args, **kwargs):  
        super().__init__(*args, **kwargs)
        #Get saved booking instance
        old_booking = self.context.get('booking', None) 

        if old_booking:
            #initialize field values/choices 
            self.fields['old_branch'].default = old_booking.branch.name
            self.fields['old_room'].default = old_booking.room.room_number
            self.fields['new_room'].queryset = Room.objects.select_related('branch').filter(branch=old_booking.branch, is_available=True).order_by('room_number')
            self.fields['new_branch'].queryset = Branch.objects.all().order_by('name')
        else:
            self.fields['new_room'].queryset = Room.objects.none()
            self.fields['new_branch'].queryset = Branch.objects.none()

    def validate(self, data):
        old_booking = self.context.get('booking') 
        guest_first_name = data.get('guest_first_name')
        guest_last_name = data.get('guest_last_name')
        guest_phone = data.get('phone_number')
        new_branch = data.get('new_branch')
        new_room = data.get('new_room')
        new_check_in = data.get('new_check_in_date')
        new_check_out = data.get('new_check_out_date')
        
        #normalize phone number 
        guest_phone_normalized = User.normalize_phone_number(guest_phone)

        #retrieve booking object 
        booking = Booking.objects.filter(
            guest_first_name=guest_first_name, 
            guest_last_name=guest_last_name, 
            phone_number=guest_phone_normalized)
        
        if not booking.exists():
            raise serializers.ValidationError('No booking with the credentials provided!')

        if old_booking.branch == new_branch and int(old_booking.room.room_number) == int(new_room.room_number):
            raise serializers.ValidationError("You're already booked in this room. Please choose a different one.")

        if not new_room.is_available:
            raise serializers.ValidationError('This room is already booked.')

        now = datetime.now().date()
        if (old_booking.check_in_date - now) < timedelta(days=1):
            raise serializers.ValidationError('Booking cannot change within 24 hours of check-in.')

        if new_check_in >= new_check_out:
            raise serializers.ValidationError('Check-out date cannot be before check-in date.')

        return data

#Change Room Serializer
class ChangeRoomSerializer(serializers.ModelSerializer):
    current_branch = serializers.CharField(read_only=True)
    old_room = serializers.CharField(read_only=True)
    new_room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.none())

    class Meta:
        model = Booking
        fields = ['current_branch', 'guest_first_name', 'guest_last_name',
                  'phone_number', 'old_room', 'new_room']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #get saved booking instance
        old_booking = self.context.get('booking', None) 

        if old_booking:
            #Initialize fields and filter rooms to only those available in the same hotel
            self.fields['current_branch'].default = old_booking.branch.name
            self.fields['old_room'].default = old_booking.room.room_number
            self.fields['new_room'].queryset = Room.objects.select_related('branch').filter(
                branch=old_booking.branch, is_available=True).order_by('room_number')
        else:
            self.fields['new_room'].queryset = Room.objects.none()

    def validate(self, data):
        old_booking = self.context.get('booking') 
        guest_first_name = data.get('guest_first_name')
        guest_last_name = data.get('guest_last_name')
        guest_phone = data.get('phone_number')
        new_room = data.get('new_room')

        #normalize phone number 
        guest_phone_normalized = User.normalize_phone_number(guest_phone)

        #retrieve booking object 
        booking = Booking.objects.filter(
            guest_first_name=guest_first_name,
            guest_last_name=guest_last_name,
            phone_number=guest_phone_normalized)
        
        if not booking.exists():
            raise serializers.ValidationError('No room booked with the credentials provided!')

        if not new_room.is_available:
            raise serializers.ValidationError('This room is already booked.')

        if int(old_booking.room.room_number) == int(new_room.room_number):
            raise serializers.ValidationError('This is the same room as before!')

        return data

#Delete Booking Serializer 
class DeleteBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['guest_first_name', 'guest_last_name', 'phone_number']

    def validate(self, data):
        guest_first_name = data.get('guest_first_name')
        guest_last_name = data.get('guest_last_name')
        guest_phone = data.get('phone_number')

        #normalize phone number 
        guest_phone_normalized = User.normalize_phone_number(guest_phone)
        data['phone_number'] = guest_phone_normalized

        try:
            booking = Booking.objects.get(guest_first_name=guest_first_name, 
                                          guest_last_name=guest_last_name,
                                          phone_number=guest_phone_normalized)
        except Booking.DoesNotExist:
            raise serializers.ValidationError('No booking found with the credentials provided.')

        #assign booking to data (to be used by the relevant view)
        data['booking'] = booking
        return data


#Other General-purpose Serializers
class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ['guest', 'is_subscribed'] 

class BookingSerializer(serializers.ModelSerializer):
    branch = serializers.PrimaryKeyRelatedField(read_only=True)
    room = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Booking 
        fields = '__all__'

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch 
        fields = ['id', 'name', 'address', 'zipcode', 'phone_number', 'email', 
                  'website', 'rating', 'branch_slug', 'branch_img']

class RoomSerializer(serializers.ModelSerializer):
    branch = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'branch', 'room_number', 'room_type', 'room_img', 
                  'price_per_night', 'is_available']


#Nested Serializers 
#Serializer for registered guest's me page
class GuestMeSerializer(serializers.Serializer):
    active_bookings = BookingSerializer(many=True)
    past_bookings = BookingSerializer(many=True)

#Serializer for previewing rooms by branch
class RoomsByBranchSerializer(serializers.Serializer):
    branch_name = serializers.CharField()
    branch_slug = serializers.CharField()
    room_samples = RoomSerializer(many=True)



