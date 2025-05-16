import datetime
from rest_framework import serializers
from .models import Category, Genre, Title

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')

class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = ('name', 'year', 'description', 'genre', 'category')

    def validate_year(self, value):
        current_year = datetime.date.today().year
        if value > current_year:
            raise serializers.ValidationError(
                f"Год не может быть больше текущего года ({current_year})."
            )
        return value

    def create(self, validated_data):
        genres_data = validated_data.pop('genre')
        category_data = validated_data.pop('category')
        category_obj, _ = Category.objects.get_or_create(**category_data)
        title = Title.objects.create(**validated_data, category=category_obj)
        for genre_data in genres_data:
            genre_obj, _ = Genre.objects.get_or_create(**genre_data)
            title.genre.add(genre_obj)
        return title

    def update(self, instance, validated_data):
        genres_data = validated_data.pop('genre')
        category_data = validated_data.pop('category')
        category_obj, _ = Category.objects.get_or_create(**category_data)
        instance.category = category_obj
        instance.save()

        instance.genre.clear()
        for genre_data in genres_data:
            genre_obj, _ = Genre.objects.get_or_create(**genre_data)
            instance.genre.add(genre_obj)
        return instance
