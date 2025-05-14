import datetime

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Category, Genre, Title


class CsvUploadSerializer(serializers.Serializer):
    """Сериализатор для загрузки CSV."""

    file = serializers.FileField()


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    name = serializers.TextField(max_length=256)
    slug = serializers.SlugField(max_length=50, unique=True)

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений."""

    genre = serializers.StringRelatedField()
    category = serializers.StringRelatedField()

    def validate_year(self, value):
        """Проверка даты создания произведения."""
        current_year = datetime.date.today().year
        if value > current_year:
            raise ValidationError(
                f"Год не может быть больше текущего года ({current_year})."
            )
        return value

    class Meta:
        model = Title
        fields = ('name', 'year', 'description', 'genre', 'category')
