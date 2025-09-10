from django.views.generic import TemplateView  
from django.urls import path 
from . import views 

urlpatterns = [
    #home url route
    path('', views.Home, name='home'),  
    
    #URLs for viewing branch details (including about and contact pages)
    path('branches/', views.PreviewBranches.as_view(), name='branches_all'),
    path('branches/<slug:branch_slug>/', views.PreviewRooms_byBranch.as_view(), name='branch_details'),
    path('branches/<slug:branch_slug>/contact-us', views.ContactUs, name='branch_contact_us'),  
    path('branches/<slug:branch_slug>/about', views.About, name='branch_about'),   
    
    #URLs for booking rooms 
    path('branches/<slug:branch_slug>/make-booking/', views.CreateBookingView.as_view(), name='create_booking'),  
    path('booking-successful/', TemplateView.as_view(template_name='booking/booking_successful.html'), name='booking_successful'),
    
    #URLs for staff members to view and modify data
    path('staff/home/', views.staff_home, name='staff_home'),
    path('staff/guest-bookings/<slug:branch_slug>/rooms/', views.DisplayBookings_byBranch.as_view(), name='bookings_by_branch'),  
    path('staff/guest-bookings/<slug:branch_slug>/<int:room_number>/', views.DisplayBookingDetail_byStaff.as_view(), name='booking_detail'),
    path('staff/guest-bookings/<slug:branch_slug>/<int:room_number>/delete/', views.DeleteBooking_byStaff.as_view(), name='delete_booking_staff'),
    path('staff/guest-bookings/delete/delete-success/', TemplateView.as_view(template_name='staff/delete_booking_successful.html'), name='delete_booking_successful_staff'),


    #URLs for guests (registered and unregistered) to view and modify data
    path('guests/', views.guest_home, name='guest_home'),
    path('guests/me/', views.guest_me, name='guest_me'),  #registered users' profiles
    path('guests/request-booking/', views.RequestBooking_guest.as_view(), name='booking_detail_request'),  
    path('guests/bookings/<int:id>/', views.DisplayBookingDetail_guest.as_view(), name='booking_detail_for_guest'),
    #URLs for changing booking
    path('guests/bookings/<slug:branch_slug>/<int:room_number>/change-booking/', views.ChangeBookingView.as_view(), name='booking_change'),
    path('guests/change-booking/success/', TemplateView.as_view(template_name='guests/booking_change_successful.html'), name='booking_change_successful'),
    #URLs for changing rooms only
    path('guests/bookings/<slug:branch_slug>/<int:room_number>/change-room/', views.ChangeRoomView.as_view(), name='room_change'),   
    path('guests/change-room/success/', TemplateView.as_view(template_name='guests/room_change_successful.html'), name='room_change_successful'),
    #urls for deleting booking
    path('guests/bookings/<slug:branch_slug>/<int:room_number>/delete-booking/', views.DeleteBooking_byGuest.as_view(), name='delete_booking_guest'),  
    path('guests/delete-booking/success/', TemplateView.as_view(template_name='guests/delete_booking_successful.html'), name='delete_booking_successful_guest'),
]


