from django.contrib import admin, messages
from .models import Booking, Branch, Room 
from datetime import date, timedelta


#Customize the Hotels table in admin 
@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    #fields to display 
    list_display = ['name', 'address', 'zipcode', 'phone_number', 'email', 'website', 'rating', 'branch_slug']

    #read-only fields
    readonly_fields = ['branch_slug',]

    #search fields 
    search_fields = ['name', 'address']

    #filtering fields 
    list_filter = ['name', 'rating']
    
    #auto-generates slug field from the name (#NOTE: might raise error)
    prepopulated_fields = {'branch_slug': ('name',)}  
    
    #table ordered by 
    ordering = ['name']


#Add custom filter for room price 
class CustomPriceFilter(admin.SimpleListFilter):
    title = 'Room Price'  #title of the filter in the sidebar
    parameter_name = 'price_range'  #adds url parameter like this: /Rooms/?price_range=your_filter_value

    def lookups(self, request, model_admin):
        lookup_options = [
            ('low', 'Cheap'),  
            ('moderate', 'Moderate'),
            ('high', 'Expensive')
        ]
        return lookup_options
    
    def queryset(self, request, queryset):
        #Identify price range label by where the prices fall
        if self.value() == 'low':
            return queryset.filter(price_per_night__lt=150)
        elif self.value() == 'moderate': 
            return queryset.filter(price_per_night__gt=150, price_per_night__lte=350)
        elif self.value() == 'high':
            return queryset.filter(price_per_night__gt=350)
        
        return queryset


#Customize the Rooms table in admin 
@admin.register(Room)
class RoomsAdmin(admin.ModelAdmin):
    #fields to display 
    list_display = ['branch', 'room_number', 'room_type', 'price_per_night', 'is_available']

    #search fields 
    search_fields = ['branch__name', '=room_number', 'room_type']

    #filtering fields 
    list_filter = ['branch', 'room_type', 'is_available', CustomPriceFilter]



#Check-in date filter 
class CheckInDateFilter(admin.SimpleListFilter):
    title = 'Check-In Date (Range)'
    parameter_name = 'check_in_range'

    def lookups(self, request, model_admin):
        return [
            ('today', 'From Today'),
            ('previous', 'Before Today'),
            ('this_month', 'This Month'),
            ('next_7_days', 'Next 7 Days'),
        ]

    def queryset(self, request, queryset):
        today = date.today()

        if self.value() == 'today':
            return queryset.filter(check_in_date__gte=today)
        elif self.value() == 'previous':
            return queryset.filter(check_in_date__lt=today)
        elif self.value() == 'this_month':
            return queryset.filter(check_in_date__month=today.month, check_in_date__year=today.year)
        elif self.value() == 'next_7_days':
            return queryset.filter(check_in_date__gte=today, check_in_date__lte=today + timedelta(days=7))
        return queryset

#Check-out date filter
class CheckOutDateFilter(admin.SimpleListFilter):
    title = 'Check-Out Date (Range)'
    parameter_name = 'check_out_range'

    def lookups(self, request, model_admin):
        return [
            ('today', 'From Today'),
            ('previous', 'Before Today'),
            ('this_month', 'This Month'),
            ('next_7_days', 'Next 7 Days'),
        ]

    def queryset(self, request, queryset):
        today = date.today()

        if self.value() == 'today':
            return queryset.filter(check_out_date__gte=today)
        elif self.value() == 'previous':
            return queryset.filter(check_out_date__lt=today)
        elif self.value() == 'this_month':
            return queryset.filter(check_out_date__month=today.month, check_out_date__year=today.year)
        elif self.value() == 'next_7_days':
            return queryset.filter(check_out_date__gte=today, check_out_date__lte=today + timedelta(days=7))
        return queryset


#Customize the Guests table in admin 
@admin.register(Booking)
class BookingsAdmin(admin.ModelAdmin):
    #fields to display 
    list_display = ['guest_first_name', 'guest_last_name', 'date_of_birth', 'gender', 'nationality', 
            'phone_number', 'email', 'branch', 'room', 'check_in_date', 'check_out_date', 'id_number']
    
    #fields that are read-only and cannot be edited by admin
    readonly_fields = ['booking_date', 'last_modified']
    
    #fields viable for searching using a search box 
    search_fields = ['^guest_first_name', '^guest_last_name', '^branch__name', 
                     '=room__room_number', 'check_in_date', 'check_out_date']

    #fields viable for filtering by 
    list_filter = ['branch', CheckInDateFilter, CheckOutDateFilter, 'booking_date', 'last_modified']
    
    #other fields that you can add to customize admin behavior
    list_per_page = 25   #number of records to display per page
    list_select_related = ('branch', 'room')   #to optimize database queries by using data JOINs (for relationship fields)

    ordering = ['-booking_date', '-last_modified'] 

    autocomplete_fields = ['branch', 'room']

    #Customize how fields appear, breaken down into two sections: guest details and room details 
    fieldsets = [
        (
            'Guest Details',
            {
                'fields': ['guest_first_name', 'guest_last_name', 'date_of_birth', 'gender', 
                           'nationality', 'phone_number', 'email', 'id_number', 'id_photo'],
            },
        ),
        (
            'Room Details',
            {
                'fields': ['branch', 'room', 'check_in_date', 'check_out_date', 'booking_date', 'last_modified'],
            },
        ),
    ]

    actions = ['remove_booking']  

    #Define custom admin action 
    @admin.action(description='Remove Booking')   #takes the descriptor seen in the dropdown menu!
    def remove_booking(self, request, queryset):
        #get guest names and room numbers for display later
        guest_first_names= list(queryset.values_list('guest_first_name', flat=True))
        guest_last_names= list(queryset.values_list('guest_last_name', flat=True))
        room_numbers = list(queryset.values_list('room', flat=True))

        #Build a message like "John Doe - room 101"
        combined_fields = [f"{guest_first} {guest_last} - Room {room}" for guest_first, guest_last, room in zip(guest_first_names, guest_last_names, room_numbers)]
        combined_message = ', '.join(combined_fields)
    
        #delete booking from the database
        removed_bookings = queryset.delete()
        
        #send success feedback message to the admin 
        self.message_user(request, f'Booking successfully removed for:  {combined_message}', messages.SUCCESS)
    
