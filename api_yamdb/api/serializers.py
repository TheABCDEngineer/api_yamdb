from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator


User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
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
                                    message='Эта электронная почта '
                                    'уже используется.')]
    )

    def validate_username(self, value):
        if value == 'me':
            raise ValidationError('Использовать имя me запрещено.')
        return value

    class Meta:
        model = User
        fields = ['username', 'email']


class UserSerializer(SignUpSerializer):
    """Сериализатор для регистрации."""

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        ]


class TokenSerializer(serializers.Serializer):
    """Сериализатор для выдачи токена."""
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        user = get_object_or_404(User, username=data.get('username'))
        data['user'] = user
        if user.confirmation_code == data.get('confirmation_code'):
            return data
        raise serializers.ValidationError('Неверный код подтверждения.')
