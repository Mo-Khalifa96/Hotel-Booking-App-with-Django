from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


#Get user model 
User = get_user_model()

#Override the login credentials to set email or phone number as default credentials 
class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            #try username as email OR as phone number
            user = User.objects.get(Q(email=username) | Q(phone_number=username))
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
    
