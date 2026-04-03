from django.utils import translation
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import APIException
from django.core.cache import cache


class UnauthorizedException(APIException):
    status_code = 401
    default_detail = 'Invalid or expired token'
    default_code = 'unauthorized'

class CustomBearerAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            raise UnauthorizedException('Authentication credentials were not provided')

        if not auth_header.startswith('Bearer '):
            raise UnauthorizedException('Bearer token were not provided')

        token = auth_header.split(' ')[1]
        user_data = cache.get(str(token))

        if not user_data:
            raise UnauthorizedException('Invalid or expired token')

        translation.activate(user_data.get('locale'))
        request.LANGUAGE_CODE = translation.get_language()

        return (user_data, token)