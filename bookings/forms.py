import re 
from django import forms 
from accounts.models import User 
from bookings.models import Room, Booking, Branch 
from datetime import datetime, timedelta
from django.db import transaction
from django.db.models import Q 


#Booking Creation form 
class BookingForm(forms.ModelForm):
    #branch name field to display current branch
    branch_name = forms.CharField(disabled=True, label="Branch Name")  #display only
    
    #customize date fields 
    date_of_birth = forms.DateField(
        input_formats=['%Y-%m-%d', '%d-%m-%Y'],
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'placeholder': 'DD-MM-YYYY', 'type': 'date'})
    )
    check_in_date = forms.DateField(
        input_formats=['%Y-%m-%d', '%d-%m-%Y'],
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'placeholder': 'DD-MM-YYYY', 'type': 'date'})
    )
    check_out_date = forms.DateField(
        input_formats=['%Y-%m-%d', '%d-%m-%Y'],
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'placeholder': 'DD-MM-YYYY', 'type': 'date'})
    )
    
    class Meta:
        model = Booking
        fields = ['guest_first_name', 'guest_last_name', 'date_of_birth', 'gender', 'nationality',
                'phone_number', 'email', 'id_number', 'id_photo', 'room', 'check_in_date', 'check_out_date']
    
    def __init__(self, *args, branch=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(['branch_name', 'guest_first_name', 'guest_last_name', 'date_of_birth', 'gender', 
                           'nationality', 'phone_number', 'email', 'id_number', 'id_photo', 'room', 'check_in_date', 
                           'check_out_date'])
        
        #get branch from the relevant view (CreateBookingView)
        if branch:
            self.current_branch = branch  #assign branch object 
            self.fields['branch_name'].initial = branch.name
            self.fields['room'].queryset = Room.objects.select_related('branch').filter(branch=branch, is_available=True)

 
    def clean_room(self):
        room = self.cleaned_data.get('room')
        if room and not room.is_available:
            raise forms.ValidationError("This room is already booked!")
        return room
    
    def clean(self):
        cleaned_data = super().clean() 
        #pass current branch back to the view 
        cleaned_data['current_branch'] = self.current_branch
        return cleaned_data


#Form to request a booking by guest 
class BookingRequestForm(forms.ModelForm):
    #add field, email or phone number 
    email_or_phone = forms.CharField(max_length=50, required=True, 
        label='Email or Phone Number', 
        widget=forms.TextInput(attrs={'placeholder': 'Enter email address or phone number'}))

    class Meta:
        model = Booking 
        fields = ['guest_first_name', 'guest_last_name']
        widgets = {
            'guest_first_name': forms.TextInput(attrs={'placeholder': 'Enter first name'}),
            'guest_last_name': forms.TextInput(attrs={'placeholder': 'Enter last name'}),
            } 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(['guest_first_name', 'guest_last_name', 'email_or_phone'])
    
    def clean(self):
        cleaned_data = super().clean()  #i.e. cleaned data up to that point
        guest_first_name = cleaned_data.get('guest_first_name')
        guest_last_name = cleaned_data.get('guest_last_name')
        guest_email_or_phone = cleaned_data.get('email_or_phone')

        #make sure all data are provided
        if not (guest_first_name and guest_last_name and guest_email_or_phone):
            return cleaned_data
        
        #validate name 
        if not Booking.objects.filter(guest_first_name__iexact=guest_first_name, guest_last_name__iexact=guest_last_name):
            raise forms.ValidationError("No booking with the name provided.")
        
        #validate email or phone number
        if '@' in guest_email_or_phone:
            if not Booking.objects.filter(email__iexact=guest_email_or_phone):
                raise forms.ValidationError('No booking with the email address provided.')
        else:
            guest_email_or_phone = User.normalize_phone_number(guest_email_or_phone)
            if not Booking.objects.filter(phone_number=guest_email_or_phone):
                raise forms.ValidationError('No booking with the phone number provided.')

        #get requested booking and pass it to cleaned data
        requested_booking = Booking.objects.filter(
            (Q(guest_first_name=guest_first_name) & Q(guest_last_name=guest_last_name)) & 
            (Q(email=guest_email_or_phone) | Q(phone_number=guest_email_or_phone))   
        ).first()

        #validate that booking exists
        if not requested_booking:
            raise forms.ValidationError("No booking found with the provided details.")
        
        #add the booking to cleaned data 
        cleaned_data['requested_booking'] = requested_booking
        return cleaned_data
    

#Form to change existing booking
class ChangeBookingForm(forms.ModelForm):
    #old branch for display only
    old_branch = forms.CharField(disabled=True, label='Current Branch',
                    widget=forms.TextInput(attrs={'readonly':'readonly'}))    
    
    #get branch choices for choosing new branch
    new_branch = forms.ModelChoiceField(   
        queryset=Branch.objects.none(),
        label="Select New Branch",
        empty_label="Select a branch",
    )

    #old room for display only 
    old_room = forms.CharField(disabled=True, label='Old Room Number')

    #get room choices for choosing new room
    new_room = forms.ModelChoiceField(    
        queryset=Room.objects.none(),
        label="Select New Room",
        empty_label="Select a room",
    )
    
    #customize date fields 
    new_check_in_date = forms.DateField(
        input_formats=['%Y-%m-%d', '%d-%m-%Y'],
        widget=forms.DateInput(format='%Y-%m-%d', 
            attrs={'type': 'date', 'placeholder': 'DD-MM-YYYY'}),
        label="New Check-in Date"
    )
    new_check_out_date = forms.DateField(
        input_formats=['%Y-%m-%d', '%d-%m-%Y'],
        widget=forms.DateInput(format='%Y-%m-%d', 
            attrs={'type': 'date', 'placeholder': 'DD-MM-YYYY'}),
        label="New Check-out Date"
    )


    class Meta:
        model = Booking
        fields = ['guest_first_name', 'guest_last_name', 'phone_number']

    #order and initialize fields above
    def __init__(self, *args, **kwargs):  
        super().__init__(*args, **kwargs)
        self.order_fields(['guest_first_name', 'guest_last_name', 'phone_number', 'old_branch', 'new_branch', 
                           'old_room', 'new_room', 'new_check_in_date', 'new_check_out_date'])
        
        #Get saved booking instance
        old_booking = self.instance  

        if old_booking:
            #initialize field values/choices 
            self.fields['old_branch'].initial = old_booking.branch.name
            self.fields['old_room'].initial = old_booking.room.room_number
            self.fields['new_room'].queryset = Room.objects.select_related('branch').filter(branch=old_booking.branch, is_available=True).order_by('room_number')
            self.fields['new_branch'].queryset = Branch.objects.all().order_by('name')


    def clean(self):
        old_booking = self.instance
        cleaned_data = super().clean()
        guest_first_name = cleaned_data.get('guest_first_name')
        guest_last_name = cleaned_data.get('guest_last_name')
        guest_phone = cleaned_data.get('phone_number')
        old_branch = old_booking.branch
        new_branch = cleaned_data.get('new_branch')
        old_room = old_booking.room
        new_room = cleaned_data.get('new_room')
        new_check_in = cleaned_data.get('new_check_in_date')
        new_check_out = cleaned_data.get('new_check_out_date')

        if not new_check_in or not new_check_out:
            return cleaned_data

        #normalize phone number
        guest_phone_normalized = User.normalize_phone_number(guest_phone)

        #fetch and check if the booking with the details provided exists in the database
        booking = Booking.objects.select_related('branch', 'room').filter(guest_first_name=guest_first_name, 
                                                                          guest_last_name=guest_last_name, 
                                                                          phone_number=guest_phone_normalized)
        
        if not booking.exists():
            raise forms.ValidationError("No booking with the credentials provided!")
        
        #check if room number is different
        if (old_branch == new_branch) and (int(old_room.room_number) == int(new_room.room_number)):
            raise forms.ValidationError("You're already booked in this room. Please choose a different one.")

        #double check if the new room is available 
        if not new_room.is_available:
            raise forms.ValidationError("This room is already booked.")        

        #Make sure booking change is at least 24 hours in advance
        now = datetime.now().date()
        if (old_booking.check_in_date - now) < timedelta(days=1):
            raise forms.ValidationError("Booking cannot change within 24 hours of check-in. Try another date.")

        if new_check_in >= new_check_out:
            raise forms.ValidationError("Check-out date cannot be set before check-in date!")

        return cleaned_data


#Room change form 
class ChangeRoomForm(forms.ModelForm):
    current_branch = forms.CharField(disabled=True, label='Current Branch')

    old_room = forms.CharField(disabled=True, label='Old Room Number')

    new_room = forms.ModelChoiceField(
        queryset=Room.objects.none(),  
        label="New Room Number",
        empty_label="Select new room number",
    )


    class Meta:
        model = Booking
        fields = ['guest_first_name', 'guest_last_name', 'phone_number']   

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #order fields 
        self.order_fields(['current_branch', 'guest_first_name', 'guest_last_name', 'phone_number', 'old_room', 'new_room'])
        
        #get saved booking instance
        old_booking = self.instance 
        if old_booking:
            #Initialize fields and filter rooms to only those available in the same hotel
            self.fields['current_branch'].initial = old_booking.branch.name
            self.fields['old_room'].initial = old_booking.room.room_number
            self.fields['new_room'].queryset = Room.objects.select_related('branch').filter(
                branch=old_booking.branch, is_available=True).order_by('room_number')


    def clean(self):
        old_booking = self.instance
        cleaned_data = super().clean()
        guest_first_name = cleaned_data.get('guest_first_name')
        guest_last_name = cleaned_data.get('guest_last_name')
        guest_phone = cleaned_data.get('phone_number')
        old_room = old_booking.room 
        new_room = cleaned_data.get('new_room')
        
        #normalize phone number
        guest_phone_normalized = User.normalize_phone_number(guest_phone)

        #fetch and check if the booking with the details provided exists in the database
        booking = Booking.objects.select_related('branch', 'room').filter(guest_first_name=guest_first_name, 
                                                                          guest_last_name=guest_last_name, 
                                                                          phone_number=guest_phone_normalized)
        
        if not booking.exists():
            raise forms.ValidationError("No room booked with the credentials provided!")

        #double check room availability 
        if not new_room.is_available:
            raise forms.ValidationError("This room is already booked.")

        #check if room number is different, belongs to the same hotel, and is available
        if (int(old_room.room_number) == int(new_room.room_number)):
            raise forms.ValidationError("This is the same room as before!")
  
        return cleaned_data  


#Form to delete existing booking
class DeleteBookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['guest_first_name', 'guest_last_name', 'phone_number']  

    def clean(self):
        cleaned_data = super().clean()
        guest_first_name = cleaned_data.get('guest_first_name')
        guest_last_name = cleaned_data.get('guest_last_name')
        guest_phone = cleaned_data.get('phone_number')

        #normalize phone number
        guest_phone_normalized = User.normalize_phone_number(guest_phone)
        cleaned_data['phone_number'] = guest_phone_normalized

        try:
            booking = Booking.objects.get(guest_first_name=guest_first_name, 
                                          guest_last_name=guest_last_name,
                                          phone_number=guest_phone_normalized)
        except Booking.DoesNotExist:
            raise forms.ValidationError("No booking found with the credentials provided.")


        #add booking object as form attribute (accessible via view)
        self.cleaned_booking = booking

        return cleaned_data



