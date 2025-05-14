from rest_framework import serializers, validators
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    class Meta:
        model = get_user_model()
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role')
