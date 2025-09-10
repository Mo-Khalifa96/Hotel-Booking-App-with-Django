import django_filters
from django_filters import FilterSet
from bookings.models import Booking, Room, Branch
from django.db.models import Q
from django import forms



#Filter for branches (not used)
class BranchFilter(FilterSet):
    name = django_filters.CharFilter(method='filter_branch_name')
    rating_min = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    rating_max = django_filters.NumberFilter(field_name='rating', lookup_expr='lte')

    def filter_branch_name(self, queryset, name, value):
        return queryset.filter(Q(name__istartswith=value) | Q(name__icontains=value))
    
    class Meta:
        model = Branch
        fields = {
            'address': ['icontains'],
            'zipcode': ['exact'],
            'website': ['icontains'],
        }


#Filter for rooms (not used)
class RoomFilter(FilterSet):
    branch = django_filters.CharFilter(field_name='branch__name', lookup_expr='icontains')
    room_number = django_filters.NumberFilter(lookup_expr='exact')
    room_type = django_filters.ChoiceFilter(choices=Room.ROOM_TYPES)
    is_available = django_filters.BooleanFilter()
    price_min = django_filters.NumberFilter(field_name='price_per_night', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price_per_night', lookup_expr='lte')

    class Meta:
        model = Room
        fields = []

#Filter for bookings
class BookingFilter(FilterSet):
    guest_first_name = django_filters.CharFilter(
        label='First Name',
        lookup_expr='istartswith',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name...'})
    )

    guest_last_name = django_filters.CharFilter(
        label='Last Name',
        lookup_expr='istartswith',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name...'})
    )

    nationality = django_filters.CharFilter(
        label='Nationality',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nationality'})
    )

    branch = django_filters.ModelChoiceFilter(
        label='Branch',
        queryset=Branch.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    room_number = django_filters.NumberFilter(
        label='Room Number', 
        field_name='room__room_number', 
        lookup_expr='exact', 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Room number'})
        )

    room_type = django_filters.CharFilter(
        label='Room Type',
        field_name='room__room_type',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Room type'})
    )

    check_in_after = django_filters.DateFilter(
        label='Check-in After',
        field_name='check_in_date',
        lookup_expr='gte',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    check_in_before = django_filters.DateFilter(
        label='Check-in Before',
        field_name='check_in_date',
        lookup_expr='lte',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    check_out_after = django_filters.DateFilter(
        label='Check-out After',
        field_name='check_out_date',
        lookup_expr='gte',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    check_out_before = django_filters.DateFilter(
        label='Check-out Before',
        field_name='check_out_date',
        lookup_expr='lte',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    booking_date = django_filters.DateFromToRangeFilter(
        label='Booking Date Range',
        field_name='booking_date',
        widget=django_filters.widgets.RangeWidget(
            attrs={'class': 'form-control', 'type': 'date'}
        )
    )

    last_modified = django_filters.DateFromToRangeFilter(
        label='Last Modified Range',
        field_name='last_modified',
        widget=django_filters.widgets.RangeWidget(
            attrs={'class': 'form-control', 'type': 'date'}
        )
    )

    class Meta:
        model = Booking
        fields = []
