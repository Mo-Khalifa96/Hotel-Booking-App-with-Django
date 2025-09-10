from rest_framework import status, generics
from rest_framework.response import Response
from bookings.models import Booking, Branch, Room
from accounts.models import User, Guest, Staff 
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from APIs.paginators import PageNumberPagination
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from APIs.permissions import StaffOnly, GuestOnly
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import NotFound
from bookings.signals import booking_updated_signal, room_changed_signal
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from APIs.filters import BookingFilter
from django.db import transaction
from APIs.serializers import *


#Custom TokenObtainPair view for creating JWT tokens
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CreateTokenSerializer

#Home page API view
class HomeAPIView(generics.ListAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [AllowAny]

    @method_decorator(cache_page(60*30))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

#Contact us page API view 
class ContactUsAPIView(generics.RetrieveAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [AllowAny]
    lookup_field = 'branch_slug'
    lookup_url_kwarg = 'branch_slug'

    def get_object(self):
        #return branch by its url slug 
        return get_object_or_404(Branch, branch_slug=self.kwargs['branch_slug'])

    @method_decorator(cache_page(60*30))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

#About us page API view 
class AboutAPIView(generics.RetrieveAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [AllowAny]
    lookup_field = 'branch_slug'
    lookup_url_kwarg = 'branch_slug'

    @method_decorator(cache_page(60*30))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

#Guest home API view 
class GuestHomeAPIView(generics.ListAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [AllowAny]

    @method_decorator(cache_page(60*30))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
#Registered guests page API view
class GuestMeAPIView(generics.GenericAPIView):
    serializer_class = BookingSerializer
    permission_classes = [GuestOnly]
    pagination_class = PageNumberPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ['check_in_date', 'check_out_date', 'booking_date']  
    ordering = ['-check_out_date']

    def get(self, request, *args, **kwargs):
        guest = Guest.objects.select_related('guest').get(guest=self.request.user)
        guest_bookings = Booking.all_objects.filter(guest_first_name=guest.guest.first_name, 
                                                    guest_last_name=guest.guest.last_name, 
                                                    phone_number=guest.guest.phone_number,
                                                    email=guest.guest.email)
        
        active_bookings = guest_bookings.filter(is_deleted=False)
        past_bookings = guest_bookings.filter(is_deleted=True)

        active_serialized = self.get_serializer(active_bookings, many=True).data
        past_serialized = self.get_serializer(past_bookings, many=True).data

        return Response({'active_bookings': active_serialized, 'past_bookings': past_serialized}, status=status.HTTP_200_OK)


#Staff Registeration API view
class StaffRegistrationAPIView(generics.CreateAPIView):
    serializer_class = StaffRegistrationSerializer
    permission_classes = [AllowAny]

    @transaction.atomic
    def perform_create(self, serializer):
        #Get validated data 
        validated_data = serializer.validated_data

        #Extract field values from validated data
        password = validated_data.pop('password1', None)
        validated_data.pop('password2', None)   #remove password2
        branch = validated_data.pop('branch', None)
        role = validated_data.pop('role', None)
        shift_time = validated_data.pop('shift_time', None)

        #Normalize phone number
        phone_number = validated_data['phone_number']
        validated_data['phone_number'] =  User.normalize_phone_number(phone_number)

        #Create User object 
        user = User.objects.create(**validated_data, is_staff=True)
        user.password = make_password(password)
        user.save()

        #Create Staff object 
        Staff.objects.create(member=user, role=role, branch=branch, shift_time=shift_time)

        serializer.instance = user

#Guest Registeration API view
class GuestRegistrationAPIView(generics.CreateAPIView):
    serializer_class = GuestRegistrationSerializer
    permission_classes = [AllowAny]

    @transaction.atomic
    def perform_create(self, serializer):
        #Get validated data 
        validated_data = serializer.validated_data

        #Extract field values from validated data
        password = validated_data.pop('password1', None)
        validated_data.pop('password2', None)   #remove password2
        is_subscribed = validated_data.pop('is_subscribed', True)

        #Normalize phone number
        phone_number = validated_data['phone_number']
        validated_data['phone_number'] =  User.normalize_phone_number(phone_number)

        #Create User object 
        user = User.objects.create(**validated_data, is_staff=False)
        user.password = make_password(password)
        user.save()

        #Create Guest object 
        Guest.objects.create(guest=user, is_subscribed=is_subscribed)

        serializer.instance = user


#Preview branches API view 
class PreviewBranchesAPIView(generics.ListAPIView):
    queryset = Branch.objects.all().order_by('name')
    serializer_class = BranchSerializer
    permission_classes = [AllowAny]

    @method_decorator(cache_page(60*15))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
#Preview rooms by single branch API view 
class PreviewRoomsByBranchAPIView(generics.ListAPIView):
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]
    lookup_field = 'branch_slug'
    lookup_url_kwarg = 'branch_slug'

    def get_queryset(self):
        branch = get_object_or_404(Branch, branch_slug=self.kwargs['branch_slug'])
        room_types = ['single', 'double', 'deluxe', 'double deluxe', 'suite']

        room_samples = []
        for r_type in room_types:
            room = Room.objects.select_related('branch').filter(branch=branch, room_type=r_type).first()
            if room:
                room_samples.append(room)

        return room_samples

    @method_decorator(cache_page(60*15))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    

#Display bookings by branch API view (for staff)
class DisplayBookings_byBranchAPIView(generics.ListAPIView):
    queryset = Branch.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [StaffOnly]
    lookup_field = 'branch_slug'
    lookup_url_kwarg = 'branch_slug'
    filterset_class = BookingFilter
    pagination_class = PageNumberPagination
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['guest_first_name', 'guest_last_name', 'room', 'check_in_date', 'check_out_date', 'booking_date', 'last_modified']  
    ordering = ['-booking_date', 'guest_first_name', 'guest_last_name']

    def get_queryset(self):
        branch = self.get_object()
        return Booking.objects.select_related('branch','room').filter(branch=branch).defer('last_modified', 'is_deleted')


#Create new booking API view
class CreateBookingAPIView(generics.CreateAPIView):
    serializer_class = CreateBookingSerializer
    permission_classes = [AllowAny]

    #pass branch object to the serializer as context data
    def get_serializer_context(self): 
        serializer_context = super().get_serializer_context()
        serializer_context['branch'] = get_object_or_404(Branch, branch_slug=self.kwargs['branch_slug'])
        return serializer_context

    @transaction.atomic
    def perform_create(self, serializer):
        #Get validated data 
        validated_data = serializer.validated_data

        #Create new booking
        #branch = get_object_or_404(Branch, branch_slug=self.kwargs['branch_slug'])
        branch = self.get_serializer_context()['branch']
        booking = Booking.objects.create(**validated_data, branch=branch)
        booking.save() 

        #update room availability 
        room = booking.room 
        room.is_available = False 
        room.save(update_fields=['is_available'])

        #assign new booking to the serializer's instance 
        serializer.instance = booking


#Request booking API view 
class RequestBookingAPIView(generics.CreateAPIView):
    serializer_class = RequestBookingSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            #Extract the requested booking from validated data
            requested_booking = serializer.validated_data['requested_booking']
            
            #return request booking by ID 
            return Response({"booking_id": requested_booking.id, 
                             "message": "Booking retrieved successfully."}, 
                             status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Display bookings by detail API view (for guests and staff)
class DisplayBookingDetailAPIView(generics.RetrieveAPIView):
    queryset = Booking.objects.select_related('branch', 'room').all()
    serializer_class = BookingSerializer

    def get_object(self):
        queryset = self.get_queryset()
        
        if self.request.user.is_authenticated and self.request.user.is_staff:
            branch_slug = self.kwargs.get('branch_slug')
            room_number = self.kwargs.get('room_number')

            if not (branch_slug and room_number):
                raise NotFound("Branch slug and room number are required for staff requests.")

            return get_object_or_404(queryset, branch__branch_slug=branch_slug, room__room_number=room_number)

        else:
            booking_id = self.kwargs.get('id')
            if not booking_id:
                raise NotFound("Booking ID is required for guest requests.")
            return get_object_or_404(queryset, id=booking_id)
            
    def get_permissions(self):
        user = self.request.user 
        if user.is_authenticated and user.is_staff:
            return [StaffOnly()]
        return [AllowAny()]

#Change booking API view 
class ChangeBookingAPIView(generics.UpdateAPIView):
    queryset = Booking.objects.select_related('branch', 'room').all()
    serializer_class = ChangeBookingSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        queryset = self.get_queryset()   
        branch_slug = self.kwargs.get('branch_slug')
        room_number = self.kwargs.get('room_number')

        return get_object_or_404(queryset, branch__branch_slug=branch_slug, room__room_number=room_number)

    #pass current booking object to serializer (from urls)
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['booking'] = self.get_object()  
        return context

    @transaction.atomic
    def perform_update(self, serializer):
        #Get guest's booking 
        booking = self.get_object()

        #Get validated data 
        validated_data = serializer.validated_data

        #extract new field values 
        new_branch = validated_data.get('new_branch')
        new_room  = validated_data.get('new_room')
        new_check_in_date  = validated_data.get('new_check_in_date')
        new_check_out_date = validated_data.get('new_check_out_date')

        #change new room's availability 
        new_room.is_available = False 
        new_room.save(update_fields=['is_available'])

        #change old room's availability 
        old_room = booking.room 
        old_room.is_available = True 
        old_room.save(update_fields=['is_available'])

        #update guest booking's details with the new data 
        booking.branch = new_branch
        booking.room = new_room
        booking.check_in_date = new_check_in_date
        booking.check_out_date = new_check_out_date
        #save changes 
        booking.save(update_fields=['branch', 'room', 'check_in_date', 'check_out_date'])

        #trigger booking update email signal 
        booking_updated_signal.send(sender=self.__class__, booking=booking)        

#Change room only API view 
class ChangeRoomAPIView(generics.UpdateAPIView):
    queryset = Booking.objects.select_related('branch', 'room').all()
    serializer_class = ChangeRoomSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        queryset = self.get_queryset()        
        branch_slug = self.kwargs.get('branch_slug')  
        room_number = self.kwargs.get('room_number')
        return get_object_or_404(queryset, branch__branch_slug=branch_slug, room__room_number=room_number)

    #pass current booking object to serializer (from urls)
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['booking'] = self.get_object()  
        return context

    @transaction.atomic
    def perform_update(self, serializer):
        #Get guest's booking 
        booking = self.get_object()

        #Fetch new room from serializer 
        new_room = serializer.validated_data.get('new_room')

        #change new room's availability 
        new_room.is_available = False 
        new_room.save(update_fields=['is_available'])

        #change old room's availability 
        old_room = booking.room 
        old_room.is_available = True 
        old_room.save(update_fields=['is_available'])

        #Change room and save 
        booking.room = new_room
        booking.save(update_fields=['room'])

        #trigger room change email signal 
        room_changed_signal.send(sender=self.__class__, booking=booking)        


#Delete booking API view (for staff and guests)
class DeleteBookingAPIView(generics.GenericAPIView):
    queryset = Booking.objects.select_related('branch', 'room').all()

    def get_permissions(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return [StaffOnly()]
        return [AllowAny()]

    def get_serializer_class(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return BookingSerializer  
        else:
            return DeleteBookingSerializer

    def get_object(self):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, 
                branch__branch_slug=self.kwargs['branch_slug'], 
                room__room_number=self.kwargs['room_number'])

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        user = self.request.user

        if user.is_authenticated and user.is_staff:
            #get booking from url (for staff)
            booking = self.get_object()

        else:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                #get booking from serializer (for guests) 
                booking = serializer.validated_data['booking']
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        #Call manager method to safely delete and update room availability
        Booking.all_objects.remove_canceled_booking(booking_id=booking.id)
        return Response({"detail": "Booking deleted successfully."}, status=status.HTTP_200_OK)

