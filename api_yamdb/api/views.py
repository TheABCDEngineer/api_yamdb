import secrets
from random import choice

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import status, exceptions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken


from .serializers import SignUpSerializer, UserSerializer
from .permissions import IsAdmin

User = get_user_model()


class SignUpView(APIView):
    """
    Вью-класс для регистрация нового пользователя.

    Права доступа: Доступно без токена.
    """

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Данные прошли базовую валидацию
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']

        # --- Проверяем, существует ли пользователь с такими username и email ---
        user_exists = User.objects.filter(
            username=username, email=email).exists()
        
        if user_exists:
            user = User.objects.get(username=username)
            self.send_confirmation_code(user.email, user.confirmation_code)
            return Response(
                {'username': username, 'email': email}, 
                status=status.HTTP_200_OK
            )

        # --- Проверка уникальности: имя занято другим пользователем ---
        if User.objects.filter(username=username).exists():
            raise exceptions.ValidationError(
                {'username': ['Данное имя уже используется']})

        # --- Проверка уникальности: email занят другим пользователем ---
        if User.objects.filter(email=email).exists():
            raise exceptions.ValidationError(
                {'email': ['Данная почта уже используется']})

        # --- Создаём нового пользователя ---
        code = secrets.token_urlsafe(16)

        user = User.objects.create(
            username=username,
            email=email,
            confirmation_code=code
        )
        self.send_confirmation_code(email, code, username)

        return Response({'username': username, 'email': email}, 
                        status=status.HTTP_200_OK)

    def send_confirmation_code(self, email, code, username):
        send_mail(
            subject='Ваш код подтверждения',
            message=f'Здравствуйте, {username}! Ваш код подтверждения: {code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )


class TokenObtainView(APIView):
    """
    Получение JWT-токена в обмен на username и confirmation code.

    Права доступа: Доступно без токена.
    """

    def post(self, request):
        username = request.data.get('username')
        code = request.data.get('confirmation_code')

        if not username or not code:
            raise exceptions.ParseError(
                'Необходимы поля username и confirmation_code')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('Пользователь не найден')

        if user.confirmation_code != code:
            raise exceptions.AuthenticationFailed('Неверный код подтверждения')

        token = AccessToken.for_user(user)
        return Response({
            'token': str(token),
        }, status=status.HTTP_200_OK)
    

class UserViewSet(viewsets.ModelViewSet):
    """Вью для работы с пользователями."""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
