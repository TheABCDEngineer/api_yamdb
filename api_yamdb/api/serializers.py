import datetime

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Category, Genre, Title


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    name = serializers.CharField(max_length=256)
    slug = serializers.SlugField(max_length=50)

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
    genre = serializers.PrimaryKeyRelatedField(queryset=Genre.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

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
