from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.validators import UniqueValidator

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя."""
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=150,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(),
                                    message='Это имя уже используется.')]
    )
    email = serializers.EmailField(
        max_length=254,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(),
                                    message='Эта эл.почта уже используется.')]
    )

    def validate_username(self, value):
        if value == 'me':
            raise ValidationError('Использовать имя "me" запрещено')
        return value

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        ]

class SignUpSerializer(UserSerializer):
    """Сериализатор для регистрации."""

    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=150,
        required=True,
    )
    email = serializers.EmailField(
        max_length=254,
        required=True,
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    class Meta:
        model = User
        fields = ['username', 'email']


class TokenSerializer(serializers.Serializer):
    """Сериализатор для выдачи токена."""

    class Meta:
        model = User
        fields = ['username', 'confirmation_code']
