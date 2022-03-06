from rest_framework import permissions

class IsExecutive(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.client_type == "Ejecutivo"

class IsTeller(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.client_type == "Cajero"

class IsBusiness(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.client_type == "Persona Moral"

class IsPerson(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.client_type == "Persona Física"

class IsClientReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.client_type in ["Persona Física", "Persona Moral"] and request.method in permissions.SAFE_METHODS
