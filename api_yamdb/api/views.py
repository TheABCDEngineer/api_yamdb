from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.permissions import IsAuthorOrReadOnly
from api.serializers import (CategorySerializer,
                             GenreSerializer, TitleSerializer)
from .models import Category, Genre, Title


class TitlePost(viewsets.ModelViewSet):
    """Обработка всех запросов к произведениям."""

    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ApiGenre(viewsets.ReadOnlyModelViewSet):
    """Обработка запросов 'GET' для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'


class ApiCategory(viewsets.ReadOnlyModelViewSet):
    """Обработка запросов 'GET' для жанров."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
