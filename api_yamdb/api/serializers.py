import datetime

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from titles.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=256,
        required=True
    )
    slug = serializers.RegexField(
        regex=r'^[-a-zA-Z0-9_]+$',
        max_length=50,
        required=True
    )

    class Meta:
        model = Category
        fields = ('name', 'slug')

    def validate_slug(self, value):
        if Category.objects.filter(slug=value).exists():
            raise serializers.ValidationError(
                f"Категория с slug '{value}' уже существует."
            )
        return value


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
        read_only_fields = (
            'id', 'rating'
        )

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

    def get_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.count() == 0:
            return 0

        summary_score = 0
        for review in reviews:
            summary_score += review.score

        return round(
            summary_score / reviews.count()
        )


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = (
            'id',
            'text',
            'author',
            'pub_date'
        )
        read_only_fields = (
            'id',
            'author',
            'review'
            'pub_date'
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    def validate(self, attrs):
        author = self.context['request'].user
        title = get_object_or_404(
            Title,
            pk=self.context['kwargs']['title_id']
        )
        try:
            _ = author.reviews.get(title=title)
            raise serializers.ValidationError(
                'Нельзя оставить более одного отзыва на произведение'
            )
        except Review.DoesNotExist:
            return super().validate(attrs)

    class Meta:
        model = Review
        fields = (
            'id',
            'text',
            'author',
            'score'
            'pub_date'
        )
        read_only_fields = (
            'id',
            'author',
            'title'
            'pub_date'
        )


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
