from rest_framework.viewsets import ModelViewSet
# from rest_framework import generics
from .permissions import HasUserPermission

class BasePermissionModelViewSet(ModelViewSet):
    permission_classes = [HasUserPermission]
    required_permissions = {}

    def get_permissions(self):
        if not isinstance(self.required_permissions, dict):
            raise TypeError("`required_permissions` must be a dictionary mapping actions to permission lists.")
        for permission_class in self.permission_classes:
            if isinstance(permission_class(), HasUserPermission):
                permission_class.required_permissions = self.required_permissions.get(self.action, [])
        return super().get_permissions()
