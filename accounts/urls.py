from django.urls import path 
from . import views 

urlpatterns = [
    #URLs for registration, log-ins, and log-outs
    #for staff members 
    path('staff/accounts/registration/', views.StaffRegistrationView.as_view(), name='staff_registration'),
    path('staff/accounts/registration-successful/', views.staff_registration_successful, name='staff_registration_successful'),
    path('staff/login/', views.StaffLoginView.as_view(), name='staff_login'), 
    path('staff/logout/', views.LogoutView, name='staff_logout'),
    #for registered guests
    path('guests/accounts/registration/', views.GuestRegistrationView.as_view(), name='guest_registration'),
    path('guests/accounts/registration-successful/', views.guests_registration_successful, name='guest_registration_successful'),
    path('guests/login/', views.GuestLoginView.as_view(), name='guest_login'), 
    path('guests/logout/', views.LogoutView, name='guest_logout'),

    #URLS for password management
    #urls for password change
    path('accounts/password-change/', views.PasswordChangeCBV.as_view(), name='password_change'),
    path('accounts/password-change/success/', views.PasswordChangeSuccessCBV.as_view(), name='password_change_success'),
    #urls for password reset
    path('accounts/password-reset/', views.PasswordResetCBV.as_view(), name='password_reset'),
    path('accounts/password-reset/email-sent/', views.PasswordResetEmailSentCBV.as_view(), name='password_reset_email_sent'),
    path('accounts/password-reset/<uidb64>/<token>/', views.PasswordResetLinkCBV.as_view(), name='password_reset_link'),
    path('accounts/password-reset/success/', views.PasswordResetSuccessCBV.as_view(), name='password_reset_success'),
]

