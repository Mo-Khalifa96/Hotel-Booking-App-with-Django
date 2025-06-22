import re
from django import forms
from django.db import transaction
from bookings.models import Branch 
from accounts.models import User, Staff, Guest
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm 


#Create a user form for staff registration
class StaffRegistrationForm(UserCreationForm):
    date_of_birth = forms.DateField(
        input_formats=['%Y-%m-%d', '%d-%m-%Y'],
        widget=forms.DateInput(format='%Y-%m-%d', 
            attrs={'placeholder': 'DD-MM-YYYY', 'type': 'date'}),
    )
    role = forms.CharField(max_length=20)
    branch = forms.ModelChoiceField(queryset=Branch.objects.all()) 
    shift_time = forms.ChoiceField(choices=(('', '---------'), ('morning', 'Morning Shift'), ('night', 'Night Shift')), required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'gender', 'date_of_birth', 
            'id_number', 'profile_picture', 'branch', 'role', 'shift_time', 'password1', 'password2']


#Create a user form for guest registration
class GuestRegistrationForm(UserCreationForm):
    date_of_birth = forms.DateField(
        input_formats=['%Y-%m-%d', '%d-%m-%Y'],
        widget=forms.DateInput(format='%Y-%m-%d',
            attrs={'placeholder': 'DD-MM-YYYY', 'type': 'date'}),
    )

    is_subscribed = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'gender', 'date_of_birth',
                  'nationality', 'id_number', 'profile_picture', 'password1', 'password2']
    

#Login Form 
class LoginForm(forms.Form):
    email_or_phone = forms.CharField(
        label='Email or Phone Number',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your email or phone number'})
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        email_or_phone = cleaned_data.get('email_or_phone')
        password = cleaned_data.get('password')

        #clean email or phone number
        if '@' in email_or_phone:
            if not User.objects.filter(email__iexact=email_or_phone):
                raise forms.ValidationError('No account with the email provided.')
        else:
            #normalize phone number 
            email_or_phone = User.normalize_phone_number(email_or_phone)
            if not User.objects.filter(phone_number=email_or_phone).exists():
                raise forms.ValidationError('No account with the phone number provided.') 

        if email_or_phone and password:
            user = authenticate(username=email_or_phone, password=password)
            if user is None:
                raise forms.ValidationError('Invalid email/phone or password.')
            
            if not user.is_active:
                raise forms.ValidationError('This account is inactive.')
            cleaned_data['user'] = user

        return cleaned_data


