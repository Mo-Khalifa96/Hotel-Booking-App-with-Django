from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied

#Define custom permissions
#Permission requiring user to be staff 
def staff_permission(user):
    if not (user.is_authenticated and user.is_staff):
        raise PermissionDenied('Permission denied. Only staff members are allowed.')
    return True 

#Permission requiring user to be guest (/not staff)
def guest_permission(user):
    if not (user.is_authenticated and not user.is_staff):
        raise PermissionDenied('Permission denied. Only registered guest users are allowed.')
    return True 

#Custom Permission Mixin for Staff CBVs 
class StaffOnlyMixin(PermissionRequiredMixin):
    login_url = reverse_lazy('staff_login')

    def has_permission(self):
        user = self.request.user 
        return user.is_athenticated and user.is_staff
