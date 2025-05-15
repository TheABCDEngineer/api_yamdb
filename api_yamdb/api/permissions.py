from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Кастомная проверка для вьюсетов.

    Только администратор может изменять или удалять контент.
    """

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.role == 'admin')