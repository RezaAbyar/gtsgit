from rest_framework import authentication, exceptions
from .utils import string_assets
from django.contrib.auth.models import User


class APIAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):

        api_key = request.META.get("HTTP_X_API_KEY")  # get the API key request header
        if not api_key:  # no username passed or empty in request headers
            return None  # authentication did not succeed
        try:
            user = User.objects.get(is_active=True, auth_token__key=api_key)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                string_assets.AUTHENTICATION_ENCOUNTERED["msg"])  # raise exception if user does not exist
        return user, None  # authentication successful
