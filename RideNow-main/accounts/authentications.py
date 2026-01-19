from django.conf import settings
from django.contrib.auth import get_user_model
import re

class CustomAuthenticationBackend:
    """
    Custom authentication backend that allows authentication with email, username, or
    Uganda phone number (+256)
    """
    def authenticate(self, request=None, username=None, password=None, **kwargs):
        # Phone pattern for Uganda numbers
        phone_pattern = re.compile(r'^\+256\d{9}$')
        
        if '@' in username:
            kwargs = {'email': username}
        elif phone_pattern.match(str(username)):
            kwargs = {'phone_number': username}
        else:
            kwargs = {'username': username}
            
        try:
            user = get_user_model().objects.get(**kwargs)
            if user.check_password(password):
                return user
            return None
        except get_user_model().DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            return None