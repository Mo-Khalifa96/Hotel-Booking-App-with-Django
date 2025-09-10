from django.contrib import admin, messages
from django.contrib import admin
from accounts.models import User, Guest, Staff, Management
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class GuestInline(admin.StackedInline):
    model = Guest
    can_delete = False
    verbose_name_plural = 'Guest Profile'
    fk_name = 'guest'


class StaffInline(admin.StackedInline):
    model = Staff
    can_delete = False
    verbose_name_plural = 'Staff Profile'
    fk_name = 'member'


class ManagementInline(admin.StackedInline):
    model = Management
    can_delete = False
    verbose_name_plural = 'Management Profile'
    fk_name = 'manager'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    #model admin is connected to 
    model = User 

    #add inlines
    inlines = [GuestInline, StaffInline, ManagementInline]

    #fields to display in admin panel 
    list_display = ['first_name', 'last_name', 'gender', 'date_of_birth', 'username', 'email', 
                    'phone_number','id_number', 'is_staff', 'is_active', 'last_login', 'date_joined']

    #fields to filter by 
    list_filter = ['last_name', 'date_of_birth', 'is_staff', 'is_active', 'date_joined']

    #fields to lookup data with 
    search_fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'id_number']

    #field to order data by 
    ordering = ['date_joined']

    #define read-only fields!
    readonly_fields = ('email', 'username')

    #Fields for editing existing users by admin 
    fieldsets = BaseUserAdmin.fieldsets + ( 
        (None, {'fields': ('phone_number', 'gender', 'date_of_birth', 'id_number')}),
        )

    #Fields for adding new users by admin 
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
    (None, {'fields': ('phone_number', 'gender', 'date_of_birth', 'id_number')}),
    )

    
    #prepopulated fields 
    prepopulated_fields = {
        'username': ['first_name', 'last_name'],
    }


    #admin actions
    actions = ['update_active_status']

    @admin.action(description='Update user\'s active status')
    def update_active_status(self, request, queryset):
        inactive_users = queryset.update(is_active=False)
        
        #send success feedback message to the admin
        self.message_user(request, 
                f'Number of users with inactive status: {inactive_users[0]}',
                messages.SUCCESS)
    

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ['guest_full_name', 'guest_email', 'is_subscribed']
    search_fields = ['guest__first_name', 'guest__last_name', 'guest__email']
    list_filter = ['is_subscribed']
    ordering = ['guest__first_name', 'guest__last_name']
    readonly_fields = ['guest']

    def guest_full_name(self, obj):
        return f"{obj.guest.first_name} {obj.guest.last_name}"
    
    def guest_email(self, obj):
        return obj.guest.email

    guest_full_name.short_description = 'Full Name'
    guest_email.short_description = 'Email'


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['member_full_name', 'member_email', 'role', 'branch', 'shift_time']
    search_fields = ['member__first_name', 'member__last_name', 'role']
    list_filter = ['role', 'branch', 'shift_time']
    ordering = ['member__first_name', 'member__last_name']
    readonly_fields = ['member']

    def member_full_name(self, obj):
        return f"{obj.member.first_name} {obj.member.last_name}"
    
    def member_email(self, obj):
        return obj.member.email

    member_full_name.short_description = 'Full Name'
    member_email.short_description = 'Email'


@admin.register(Management)
class ManagementAdmin(admin.ModelAdmin):
    list_display = ['manager_full_name', 'manager_email', 'management_level', 'branch']
    search_fields = ['manager__first_name', 'manager__last_name', 'management_level']
    list_filter = ['management_level', 'branch']
    ordering = ['manager__first_name', 'manager__last_name']
    readonly_fields = ['manager']

    def manager_full_name(self, obj):
        return f"{obj.manager.first_name} {obj.manager.last_name}"
    
    def manager_email(self, obj):
        return obj.manager.email

    manager_full_name.short_description = 'Full Name'
    manager_email.short_description = 'Email'
