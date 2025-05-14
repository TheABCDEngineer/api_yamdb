import csv
from io import TextIOWrapper

from rest_framework import status, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import IsAuthorOrReadOnly
from api.serializers import (CategorySerializer, CsvUploadSerializer,
                             GenreSerializer, TitleSerializer)
from .models import Category, Genre, Title


class CsvImportAPIView(APIView):
    def post(self, request):
        serializer = CsvUploadSerializer(data=request.data)
        if serializer.is_valid():
            csv_file = serializer.validated_data['file']
            decoded_file = TextIOWrapper(csv_file.file, encoding='utf-8')
            reader = csv.DictReader(decoded_file)

            for row in reader:
                genre_obj, _ = Genre.objects.get_or_create(name=row['genre'])
                category_obj, _ = Category.objects.get_or_create(
                    name=row['category']
                )
                Title.objects.create(
                    name=row['name'],
                    year=int(row['year']),
                    description=row['description'],
                    genre=genre_obj,
                    category=category_obj
                )
            return Response({"status": "Данные успешно импортированы"})
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


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


class ApiCategory(viewsets.ReadOnlyModelViewSet):
    """Обработка запросов 'GET' для жанров."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
