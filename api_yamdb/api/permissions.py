from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission, SAFE_METHODS

User = get_user_model()


class IsAuthorOrReadOnly(BasePermission):
    """Разрешает редактирование только автору объекта."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
        )


class AdminOnly(BasePermission):
    """Кастомная проверка для вьюсетов.

    Только администратор может изменять или удалять контент.
    """

    def has_permission(self, request, view):
        """
        Вызывается до выборки объекта.

        Позволяет:
        - Все безопасные методы
        - Только админам и суперпользователям — небезопасные методы
        """
        if not request.user or not request.user.is_authenticated:
            return False
        return bool(
            request.user.role == User.ADMIN
            or request.user.is_superuser
        )
