from rest_framework.permissions import BasePermission
from django.core.cache import cache


class HasUserPermission(BasePermission):
    required_permissions = []
    def has_permission(self, request, view):
        token = request.auth
        user_data = cache.get(str(token))
        if not user_data:
            return False
        elif user_data.get('is_superuser'):
            return True
        else:
            permissions = set(user_data.get('permissions', []))

        required_permissions = self.required_permissions
        if not required_permissions:
            return True

        return any(perm in permissions for perm in required_permissions)

class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.get('is_superuser', False))