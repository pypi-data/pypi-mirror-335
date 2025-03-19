from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import BaseAuthentication


class OAuth2MockAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token_info = {
            "access_token" : "ACCESS_TOKEN",
            "user_id" : 1,
            "user_first_name": "Test",
            "user_last_name": "User",
            "user_email": "test_user@nomail.com"
        }
        return AnonymousUser, token_info