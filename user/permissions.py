from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class IsUserAllIsAuthenticatedReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return bool(request.method in SAFE_METHODS or request.user == obj)


class AnonOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return not bool(request.user and request.user.is_authenticated)
