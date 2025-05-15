from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import AuthenticationFailed

from django.contrib.auth import get_user_model # TODO 3422222222222222222222222222222222222

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    username = serializers.RegexField(
        r'^[\w.@+-]+$',
        max_length=150, 
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='Данное имя уже используется'
        )
    ])

    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='Данная почта уже используется'
        )
    ])

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" запрещено')

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role')
        
    def create(self, validated_data):
        import secrets
        code = secrets.token_urlsafe(16)

        user, created = User.objects.get_or_create(
            username=validated_data['username'],
            defaults={'email': validated_data['email']}
        )

        if not created:
            user.email = validated_data['email']
        user.confirmation_code = code
        user.save()

        return user


# class SignUpSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['username', 'email']

#     def create(self, validated_data):
#         user = User.objects.create(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             confirmation_code=self.generate_confirmation_code(),
#             is_active=False  # Пользователь не активен до подтверждения
#         )
#         # Здесь можно отправить код по email
#         self.send_confirmation_email(user)
#         return user

#     def generate_confirmation_code(self):
#         import random
#         return str(random.randint(100000, 999999))

#     def send_confirmation_email(self, user):
#         # Пример простой отправки кода на email
#         print(f"Код подтверждения для {user.username}: {user.confirmation_code}")

# class TokenObtainSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     confirmation_code = serializers.CharField()

#     def validate(self, data):
#         username = data.get('username')
#         code = data.get('confirmation_code')

#         try:
#             user = User.objects.get(username=username)
#         except User.DoesNotExist:
#             raise AuthenticationFailed('Пользователь не найден.')

#         if user.confirmation_code != code:
#             raise AuthenticationFailed('Неверный код подтверждения.')

#         return {'token': str(user.tokens()['access'])}