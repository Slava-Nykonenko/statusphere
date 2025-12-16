from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class IsAuthorAllIsAuthenticatedReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(request.method in SAFE_METHODS or request.user.id == obj.author.id)
