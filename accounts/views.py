from django.conf import settings
from django.db import transaction
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from accounts.models import User, Staff, Guest 
from django.contrib.auth import views as auth_views
from django.shortcuts import render, redirect
from accounts.signals import password_reset_successful_signal
from django.views.generic.edit import FormView
from accounts.forms import (LoginForm,
                            StaffRegistrationForm,
                            GuestRegistrationForm)


#Custom function to get login url
def get_login_url(is_staff):
    protocol = settings.SITE_PROTOCOL 
    domain = settings.SITE_DOMAIN 
    path = '/staff/login/' if is_staff else '/guests/login/'
    return f"{protocol}://{domain}{path}"


#Define staff registration view
class StaffRegistrationView(FormView):
    template_name = 'registration.html'
    form_class = StaffRegistrationForm
    success_url = reverse_lazy('staff_registration_successful')

    @transaction.atomic 
    def form_valid(self, form):
        user = form.save(commit=False) #don't save yet 
        #set is_staff to True 
        user.is_staff = True 
        
        #normalize phone number 
        phone_number = form.cleaned_data.get('phone_number')
        user.phone_number = User.normalize_phone_number(phone_number)

        #save user object 
        user.save() 

        #Create new staff object
        Staff.objects.create(member=user, 
                            role=form.cleaned_data['role'], 
                            branch=form.cleaned_data['branch'], 
                            shift_time=form.cleaned_data['shift_time'])  
    
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Staff Registration'
        context['login_url'] = reverse_lazy('staff_login')
        context['registration_form'] = context['form'] 
        return context


#Define guest registration view
class GuestRegistrationView(FormView):
    template_name = 'registration.html'
    form_class = GuestRegistrationForm
    success_url = reverse_lazy('guest_registration_successful')

    @transaction.atomic 
    def form_valid(self, form):
        user = form.save(commit=False) #don't save yet 
        user.is_staff = False 
        phone_number = form.cleaned_data.get('phone_number')
        user.phone_number = User.normalize_phone_number(phone_number)

        #save user 
        user.save()

        #create new Guest object
        Guest.objects.create(guest=user, is_subscribed=form.cleaned_data.get('is_subscribed', True))

        return super().form_valid(form)

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Guest Registration'
        context['login_url'] = reverse_lazy('guest_login')
        context['registration_form'] = context['form']
        return context

#Define registration success view for staff
def staff_registration_successful(request):
    return render(request, 'registration_successful.html', context={'login_url': get_login_url(is_staff=True)})

#Define registration success view for guests
def guests_registration_successful(request):
    return render(request, 'registration_successful.html', context={'login_url': get_login_url(is_staff=False)})


#Define Log-in views for staff and registered guests
#For staff members 
class StaffLoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy('staff_home')

    #validate form and login user
    def form_valid(self, form):
        user = form.cleaned_data.get('user')
        login(self.request, user)
        return super().form_valid(form)

    #pass context data to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Staff Login'
        context['register_as'] = 'Register as Staff'
        context['registration_url'] = reverse_lazy('staff_registration')
        context['login_form'] = context['form'] 
        return context

#For registered guests
class GuestLoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy('guest_me')

    #validate form and login user
    def form_valid(self, form):
        user = form.cleaned_data.get('user')
        login(self.request, user)
        return super().form_valid(form)

    #pass context data to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Guest Login'
        context['register_as'] = 'Register as a VIP Guest'
        context['registration_url'] = reverse_lazy('guest_registration')
        context['login_form'] = context['form']
        return context

#Define log-out view 
def LogoutView(request):
    logout(request)
    return redirect('/')  #returns to home page 


#PASSWORD MANAGEMENT CBVs
#CBV for rendering password change template
class PasswordChangeCBV(auth_views.PasswordChangeView):
    template_name = 'password_change_form.html'
    success_url = reverse_lazy('password_change_success')

#CBV for rendering success page after password change
class PasswordChangeSuccessCBV(auth_views.PasswordChangeDoneView):
    template_name = 'password_change_success.html'

#CBV for rendering password reset template to take user's email address
#(as well as sending the email with the template specified!)
class PasswordResetCBV(auth_views.PasswordResetView):
    template_name = 'password_reset_form.html'
    email_template_name = 'emails/password_reset_token_email.html'
    subject_template_name = 'emails/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_email_sent') 

#CBV for rendering email success message after sending email
class PasswordResetEmailSentCBV(auth_views.PasswordResetDoneView):
    template_name = 'password_reset_email_sent.html'

#CBV for setting new password as redirected by email's link & token
class PasswordResetLinkCBV(auth_views.PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_success')

    def form_valid(self, form):
        user = form.user
        if user:
            self.request.session['password_reset_email'] = user.email
            self.request.session['first_name'] = user.first_name
            self.request.session['last_name'] = user.last_name
            self.request.session['is_staff'] = user.is_staff
        return super().form_valid(form)

#CBV for rendering success page after password reset
class PasswordResetSuccessCBV(auth_views.PasswordResetCompleteView):
    template_name = 'password_reset_success.html'

    def dispatch(self, request, *args, **kwargs):
        #get user info from session
        user_email = request.session.get('password_reset_email')
        first_name = request.session.get('first_name')
        last_name = request.session.get('last_name')
        is_staff = request.session.get('is_staff')
        try:
            if user_email:
                password_reset_successful_signal.send(sender=self.__class__, 
                is_staff=is_staff, first_name=first_name, last_name=last_name, 
                email=user_email)
        finally:
            #delete session data 
            for key in ('password_reset_email', 'first_name', 'last_name', 'is_staff'):
                request.session.pop(key, None)
            
        return super().dispatch(request, *args, **kwargs)
