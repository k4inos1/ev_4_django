"""
Sistema de permisos por roles
"""

from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Solo administradores"""

    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsSupervisorOrAdmin(permissions.BasePermission):
    """Supervisores y administradores"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and (
            request.user.is_staff or hasattr(request.user, "is_supervisor")
        )


class IsTechnicianOrReadOnly(permissions.BasePermission):
    """Técnicos pueden ver, solo admin puede modificar"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class CanModifyOwnTasks(permissions.BasePermission):
    """Técnicos solo pueden modificar sus propias tareas"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_staff:
            return True

        return obj.tecnico_asignado == request.user.username
