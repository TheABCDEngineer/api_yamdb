import secrets

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken
from .permissions import AdminOnly, IsAuthorOrReadOnly
from .serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer,
    ReviewSerializer, SignUpSerializer, TitleSerializer,
    TokenSerializer, UserSerializer,
)
from titles.models import Category, Genre, Review, Title

User = get_user_model()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        return self.__get_request_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.__get_request_review()
        )

    def __get_request_review(self):
        _ = get_object_or_404(
            Title,
            pk=self.kwargs['title_id']
        )
        return get_object_or_404(
            Review,
            pk=self.kwargs['review_id']
        )


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        return self.__get_request_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.__get_request_title()
        )

    def __get_request_title(self):
        return get_object_or_404(
            Title,
            pk=self.kwargs['title_id']
        )


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = LimitOffsetPagination


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        elif self.action in ['create', 'destroy', 'partial_update', 'update']:
            return [AdminOnly()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        elif self.action in ['create', 'destroy', 'partial_update', 'update']:
            return [AdminOnly()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


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

        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')

        user_exists = User.objects.filter(
            username=username, email=email).exists()

        if user_exists:
            user = User.objects.get(username=username)
            self.send_confirmation_code(
                user.email, user.confirmation_code, user.username)
            return Response(
                {'username': username, 'email': email},
                status=status.HTTP_200_OK
            )

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
        """Логика отправки письма с confirmation_code."""
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
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = AccessToken.for_user(serializer.validated_data.get('user'))
        return Response({
            'token': str(token),
        }, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AdminOnly]
    lookup_field = 'username'

    @action(detail=False, methods=['get', 'patch'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        """Логика для эндпоинта /me/ ."""
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = self.get_serializer(user, data=request.data,
                                             partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
