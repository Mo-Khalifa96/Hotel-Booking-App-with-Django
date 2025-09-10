from rest_framework.permissions import BasePermission

class StaffOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated: 
            if not request.user.is_staff:
                return False 
            else:
                return True
        else:
            return False 

class GuestOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated: 
            if request.user.is_staff:
                return False 
            else:
                return True
        else:
            return False 
