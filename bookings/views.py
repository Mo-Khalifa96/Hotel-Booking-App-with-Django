from django.db import transaction
from django.urls import reverse, reverse_lazy
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from .forms import BookingForm, ChangeBookingForm, ChangeRoomForm, DeleteBookingForm, BookingRequestForm
from bookings.permissions import guest_permission, staff_permission, StaffOnlyMixin
from bookings.signals import booking_updated_signal, room_changed_signal
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models import User, Guest
from bookings.models import Booking, Branch, Room
from django_filters.views import FilterView
from bookings.filters import BookingFilter




#Define home page view 
cache_page(60*30)   #caching every 30 minutes
def Home(request):
    branches_list = Branch.objects.all()
    return render(request, 'home.html', context={'branches_list': branches_list})  

#Define contacts view
@cache_page(60*30) 
def ContactUs(request, branch_slug):
    branch = get_object_or_404(Branch, branch_slug=branch_slug)
    return render(request, 'branches/contact_us.html', {'branch': branch})

#Define about view 
@cache_page(60*30)   
def About(request, branch_slug):
    return render(request, 'branches/about.html', context={'branch_slug': branch_slug})

#Define the staff home view 
@login_required(login_url=reverse_lazy('staff_login'))
@user_passes_test(staff_permission, login_url=reverse_lazy('staff_login'))
def staff_home(request):
    branches = Branch.objects.all()
    return render(request, 'staff/staff_home.html', {'branches': branches})

#Define guest home view
@cache_page(60*30)
def guest_home(request):
    branches = Branch.objects.all()
    return render(request, 'guests/guest_home.html', {'branches': branches})  

#Define guest profile view 
@login_required(login_url=reverse_lazy('guest_login'))
@user_passes_test(guest_permission, login_url=reverse_lazy('guest_login'))
def guest_me(request):
    #get registered user's data 
    guest = Guest.objects.get(guest=request.user)
    # first_name = request.user.first_name
    # last_name = request.user.last_name
    # phone_number = request.user.phone_number 
    
    #fetch registered guest's booking history 
    guest_bookings = Booking.all_objects.filter(guest_first_name=guest.guest.first_name, 
                                                guest_last_name=guest.guest.last_name, 
                                                phone_number=guest.guest.phone_number,
                                                email=guest.guest.email)
    active_bookings = guest_bookings.filter(is_deleted=False) 
    past_bookings = guest_bookings.filter(is_deleted=True)
    return render(request, 'guests/guest_me.html', {'active_bookings': active_bookings, 'past_bookings': past_bookings})


#CBV to preview list of branches
@method_decorator(cache_page(60*15), name='dispatch')
class PreviewBranches(ListView):
    model = Branch 
    template_name = 'branches/preview_branches.html'
    context_object_name = 'branches_list'  #variable name used by template

    def get_queryset(self):    
        return Branch.objects.all()

#Define CBV to preview room types per branch 
@method_decorator(cache_page(60*15), name='dispatch')
class PreviewRooms_byBranch(TemplateView):
    template_name = 'branches/preview_room_types.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        branch_slug = self.kwargs.get('branch_slug')
        branch = get_object_or_404(Branch, branch_slug=branch_slug)

        room_types = ['single', 'double', 'deluxe', 'double deluxe', 'suite']
        room_samples = []
        for r_type in room_types:
            room = Room.objects.select_related('branch').filter(branch=branch, room_type=r_type).first()
            if room:
                room_samples.append(room)

        context['branch'] = branch
        context['room_samples'] = room_samples
        return context
    
#CLASS VIEWS FOR STAFF MEMBERS TO VIEW AND MODIFY DATA 
#CBV for displaying bookings for a given branch 
class DisplayBookings_byBranch(FilterView, LoginRequiredMixin, StaffOnlyMixin):  
    model = Booking
    template_name = 'staff/bookings_list.html'
    context_object_name = 'bookings_list'  
    ordering = ['-booking_date', 'guest_first_name', 'guest_last_name']
    paginate_by = 12
    filterset_class = BookingFilter

    #override to identify branch by its url slug 
    def get_queryset(self):
        #return booking per individual branch (using url)
        branch = get_object_or_404(Branch, branch_slug=self.kwargs['branch_slug'])  
        return Booking.objects.select_related('branch', 'room').filter(branch=branch).defer('last_modified', 'is_deleted')

    #Override to pass the branch object to template (from url)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['branch'] = get_object_or_404(Branch, branch_slug=self.kwargs['branch_slug'])
        return context

#CBV for displaying details of one particular booking 
class DisplayBookingDetail_byStaff(DetailView, LoginRequiredMixin, StaffOnlyMixin):   
    model = Booking  
    template_name = 'staff/booking_detail.html' 
    context_object_name = 'booking_detailed'  
    
    def get_object(self):
        #fetch booking object from url keywords for branch slug and room number
        branch_slug = self.kwargs['branch_slug']  
        room_number = self.kwargs['room_number']  
        booking = get_object_or_404(Booking.objects.select_related('branch', 'room'), 
                    branch__branch_slug=branch_slug, room__room_number=room_number)
        return booking 
       
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #add branch instance to the template
        context['branch'] = get_object_or_404(Branch, branch_slug=self.kwargs['branch_slug'])
        return context

#Define CBV to delete booking (used by staff)
class DeleteBooking_byStaff(DeleteView, LoginRequiredMixin, StaffOnlyMixin):  
    model = Booking  
    template_name = 'staff/delete_booking.html' 
    context_object_name = 'delete_booking_form' 
    success_url = reverse_lazy('delete_booking_successful_staff') 
    
    #get particular booking object for deletion
    def get_object(self):
        #fetch booking object from url keywords for branch slug and room number
        branch_slug = self.kwargs['branch_slug']  
        room_number = self.kwargs['room_number']  
        booking = get_object_or_404(Booking.objects.select_related('branch', 'room'), 
                    branch__branch_slug=branch_slug, room__room_number=room_number)
        return booking 
    
    #add branch object to the context data 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['branch'] = get_object_or_404(Branch, branch_slug=self.kwargs['branch_slug'])
        return context

    #override the delete method to perform soft deletion only
    def delete(self, request, *args, **kwargs):
        #get current booking 
        booking = self.get_object()  
        #change room availability 
        room = booking.room
        room.is_available = True 
        room.save() 

        #Call the manager method to delete the canceled booking and change room availability
        Booking.all_objects.remove_canceled_booking(booking_id=booking.id)

        return super().delete(request, *args, **kwargs)
    

#CBV FOR CREATING BOOKING
#Define CBV for creating a new booking 
class CreateBookingView(CreateView):  
    model = Booking
    form_class = BookingForm
    template_name = 'booking/booking_form.html'  
    success_url = reverse_lazy('booking_successful')

    #pass branch object to the form (accessible via its __init__() method)
    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['branch'] = get_object_or_404(Branch, branch_slug=self.kwargs['branch_slug']) 
        return form_kwargs
    
    @transaction.atomic 
    def form_valid(self, form):
        #get new booking and set branch 
        new_booking = form.save(commit=False)
        new_booking.branch = form.cleaned_data['current_branch']
        
        #normalize phone number and save it to booking 
        phone_number = form.cleaned_data.get('phone_number')
        new_booking.phone_number = User.normalize_phone_number(phone_number)

        #save new booking 
        new_booking.save()

        #change room availability and save
        new_room = new_booking.room
        new_room.is_available = False 
        new_room.save(update_fields=['is_available'])

        return super().form_valid(form)

    #pass form as context data to the template (renaming to 'booking_form')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['booking_form'] = context.get('form')  
        return context


#CLASS VIEWS FOR GUESTS TO VIEW AND MODIFY DATA 
#Define CBV to request a booking as a guest
class RequestBooking_guest(FormView):
    form_class = BookingRequestForm
    template_name = 'guests/booking_request.html'

    def form_valid(self, form):
        #get booking from the form 
        self.current_booking = form.cleaned_data['requested_booking']
        return super().form_valid(form)

    #redirect to guest's booking with booking id 
    def get_success_url(self):
        return reverse('booking_detail_for_guest', kwargs={'id': self.current_booking.id})


#Define CBV to render the details of the booking requested 
class DisplayBookingDetail_guest(DetailView):
    model = Booking
    template_name = 'guests/booking_detail.html'
    context_object_name = 'requested_booking'
    pk_url_kwarg = 'id'  


#CBV to change existing booking 
class ChangeBookingView(UpdateView):   
    model = Booking 
    form_class = ChangeBookingForm   
    template_name = 'guests/booking_change.html' 
    context_object_name = 'booking_change_form'  
    success_url = reverse_lazy('booking_change_successful')  

    #get particular booking for updating
    def get_object(self):
        #fetch booking object from url keywords for branch slug and room number
        branch_slug = self.kwargs['branch_slug']  
        room_number = self.kwargs['room_number']  
        booking = get_object_or_404(Booking.objects.select_related('branch', 'room'), 
                    branch__branch_slug=branch_slug, room__room_number=room_number)
        return booking 

    @transaction.atomic 
    def form_valid(self, form):
        #get current booking instance from the form
        booking = form.save(commit=False)  #don't save yet
        
        #Get new booking details from the form (using cleaned_data)
        new_branch = form.cleaned_data.get('new_branch')
        new_room = form.cleaned_data.get('new_room')
        new_check_in_date = form.cleaned_data.get('new_check_in_date')
        new_check_out_date = form.cleaned_data.get('new_check_out_date')

        #change new room's availability and save 
        new_room.is_available = False 
        new_room.save(update_fields=['is_available'])   

        #Change old room's availability and save 
        old_room = booking.room
        old_room.is_available = True 
        old_room.save(update_fields=['is_available'])  

        #Change existing booking's details with the new details 
        booking.branch = new_branch 
        booking.room = new_room 
        booking.check_in_date = new_check_in_date
        booking.check_out_date = new_check_out_date

        #save changes
        booking.save(update_fields=['branch', 'room', 'check_in_date', 'check_out_date'])
        
        #Trigger booking update email signal
        booking_updated_signal.send(sender=self.__class__, booking=booking)
        
        return super().form_valid(form)

    #pass context data to the template 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['booking'] = self.get_object()
        context['booking_change_form'] = context.get('form') 
        return context


#CBV to change room for registered guests 
class ChangeRoomView(UpdateView): 
    model = Booking 
    form_class = ChangeRoomForm    
    template_name = 'guests/room_change.html'  
    context_object_name = 'room_change_form' 
    success_url = reverse_lazy('room_change_successful') 
    
    #get particular booking to change room
    def get_object(self):
        #fetch booking object from url keywords for branch slug and room number
        branch_slug = self.kwargs['branch_slug']  
        room_number = self.kwargs['room_number']  
        booking = get_object_or_404(Booking.objects.select_related('branch', 'room'), 
                    branch__branch_slug=branch_slug, room__room_number=room_number)
        return booking 

    @transaction.atomic  
    def form_valid(self, form):
        #get current booking object from the form before saving
        booking = form.save(commit=False) 
        
        #Get new room object from the form
        new_room = form.cleaned_data.get('new_room')

        #change new room's availability and save 
        new_room.is_available = False 
        new_room.save(update_fields=['is_available'])

        #Change old room's availability and save 
        old_room = booking.room
        old_room.is_available = True 
        old_room.save(update_fields=['is_available']) 

        #Change room and save 
        booking.room = new_room 
        booking.save(update_fields=['room'])        

        #Trigger room change email signal
        room_changed_signal.send(sender=self.__class__, booking=booking, old_room=old_room)

        return super().form_valid(form)


#CLASS VIEW FOR DELETING EXISTING BOOKING 
#Define CBV to delete current booking (used by Guest)
class DeleteBooking_byGuest(FormView):   
    form_class = DeleteBookingForm
    template_name = 'guests/delete_booking.html'
    success_url = reverse_lazy('delete_booking_successful_guest')

    def form_valid(self, form):
        #get booking object from form
        booking = form.cleaned_booking

        #Call the manager method to delete the canceled booking and change room availability
        Booking.all_objects.remove_canceled_booking(booking_id=booking.id)

        return super().form_valid(form)
    
