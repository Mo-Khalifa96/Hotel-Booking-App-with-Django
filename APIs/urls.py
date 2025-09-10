from django.urls import path
from APIs import views 
from djoser.views import UserViewSet
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView, TokenBlacklistView

urlpatterns = [
    #Djoser URLs  
    #JWT authentication urls (Djoser based)
    path('auth/token/create/', views.CustomTokenObtainPairView.as_view(), name='token_create'),   #for login
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/token/destroy/', TokenBlacklistView.as_view(), name='token_destroy'),  

    #Account management urls
    path('accounts/password-change/', UserViewSet.as_view({'post': 'set_password'}), name='api_password_change'),     #used by logged in users 
    path('accounts/password-reset/', UserViewSet.as_view({'post': 'reset_password'}), name='api_password_reset'),   #used by logged out users (takes email input)
    path('accounts/reset-password/<uidb64>/<token>/', UserViewSet.as_view({'post': 'reset_password_confirm'}), name='api_password_reset_confirm'),

    #Home page URL 
    path('', views.HomeAPIView.as_view(), name='api_home'), 
    
    #URLs for viewing branch details (including about and contact pages)
    path('branches/', views.PreviewBranchesAPIView.as_view(), name='api_branches_all'),
    path('branches/<slug:branch_slug>/', views.PreviewRoomsByBranchAPIView.as_view(), name='api_branch_details'),
    path('branches/<slug:branch_slug>/contact-us/', views.ContactUsAPIView.as_view(), name='api_branch_contact_us'),  
    path('branches/<slug:branch_slug>/about/', views.AboutAPIView.as_view(), name='api_branch_about'),   

    #URLs for registration
    path('staff/accounts/registration/', views.StaffRegistrationAPIView.as_view(), name='api_staff_registration'),
    path('guests/accounts/registration/', views.GuestRegistrationAPIView.as_view(), name='api_guest_registration'),

    #URL for booking 
    path('branches/<slug:branch_slug>/make-booking/', views.CreateBookingAPIView.as_view(), name='api_create_booking'),  
    
    #URLs for staff members to view and modify data
    path('staff/guest-bookings/<slug:branch_slug>/rooms/', views.DisplayBookings_byBranchAPIView.as_view(), name='api_bookings_by_branch'),  
    path('staff/guest-bookings/<slug:branch_slug>/<int:room_number>/', views.DisplayBookingDetailAPIView.as_view(), name='api_booking_detail'),
    path('staff/guest-bookings/<slug:branch_slug>/<int:room_number>/delete/', views.DeleteBookingAPIView.as_view(), name='api_delete_booking_staff'),

    #URLs for guests (registered and unregistered) to view and modify data
    path('guests/', views.GuestHomeAPIView.as_view(), name='api_guest_home'),
    path('guests/me/', views.GuestMeAPIView.as_view(), name='api_guest_me'),  #registered users' profiles
    path('guests/request-booking/', views.RequestBookingAPIView.as_view(), name='api_booking_detail_request'),  
    path('guests/bookings/<int:id>/', views.DisplayBookingDetailAPIView.as_view(), name='api_booking_detail_for_guest'),
    path('guests/bookings/<slug:branch_slug>/<int:room_number>/change-booking/', views.ChangeBookingAPIView.as_view(), name='api_booking_change'),
    path('guests/bookings/<slug:branch_slug>/<int:room_number>/change-room/', views.ChangeRoomAPIView.as_view(), name='api_room_change'),   
    path('guests/bookings/<slug:branch_slug>/<int:room_number>/delete-booking/', views.DeleteBookingAPIView.as_view(), name='dapi_elete_booking_guest'),  

]

