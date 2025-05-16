from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import User

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

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or request.user.role == User.ADMIN)
