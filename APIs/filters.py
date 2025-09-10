from django.db.models import Q
from bookings.models import Booking, Room, Branch
from django_filters import (FilterSet, ChoiceFilter, CharFilter, NumberFilter, 
                           BooleanFilter, ModelChoiceFilter, DateFilter, DateFromToRangeFilter)


#Filter for branches
class BranchFilter(FilterSet):
    name = CharFilter(method='filter_branch_name')
    rating_min = NumberFilter(field_name='rating', lookup_expr='gte')
    rating_max = NumberFilter(field_name='rating', lookup_expr='lte')

    def filter_branch_name(self, queryset, name, value):
        return queryset.filter(Q(name__istartswith=value) | Q(name__icontains=value))
    
    class Meta:
        model = Branch
        fields = {
            'address': ['icontains'],
            'zipcode': ['exact'],
            'website': ['icontains'],
        }


#Filter for rooms
class RoomFilter(FilterSet):
    branch = CharFilter(field_name='branch__name', lookup_expr='icontains')
    room_number = NumberFilter(lookup_expr='exact')
    room_type = ChoiceFilter(choices=Room.ROOM_TYPES)
    is_available = BooleanFilter()
    price_min = NumberFilter(field_name='price_per_night', lookup_expr='gte')
    price_max = NumberFilter(field_name='price_per_night', lookup_expr='lte')

    class Meta:
        model = Room
        fields = ['branch', 'room_number', 'room_type', 'is_available', 'price_min', 'price_max']


#Filter for bookings  
class BookingFilter(FilterSet):
    guest_first_name = CharFilter(field_name='guest_first_name', lookup_expr='istartswith')
    guest_last_name = CharFilter(field_name='guest_last_name', lookup_expr='istartswith')
    nationality = CharFilter(field_name='nationality', lookup_expr='icontains')
    branch = ModelChoiceFilter(field_name='room__branch', queryset=Branch.objects.all())
    room_number = NumberFilter(field_name='room__room_number', lookup_expr='exact')
    room_type = ChoiceFilter(field_name='room__room_type', choices=Room.ROOM_TYPES)
    check_in_after = DateFilter(field_name='check_in_date', lookup_expr='gte')
    check_in_before = DateFilter(field_name='check_in_date', lookup_expr='lte')
    check_out_after = DateFilter(field_name='check_out_date', lookup_expr='gte')
    check_out_before = DateFilter(field_name='check_out_date', lookup_expr='lte')
    booking_date_range = DateFromToRangeFilter(field_name='booking_date')
    last_modified_range = DateFromToRangeFilter(field_name='last_modified')

    class Meta:
        model = Booking
        fields = []  