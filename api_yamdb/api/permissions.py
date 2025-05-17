from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission, SAFE_METHODS

# from .models import User

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
        return bool(
            request.method in SAFE_METHODS or request.user.role == User.ADMIN or request.user.is_superuser
        )

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or request.user.role == User.ADMIN)
