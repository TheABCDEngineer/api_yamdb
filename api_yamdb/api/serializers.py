import datetime

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from titles.models import Category, Comment, Genre, GenreTitle, Review, Title

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
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
        read_only_fields = (
            'id', 'rating', 'genre', 'category'
        )

    def validate_year(self, value):
        current_year = datetime.date.today().year
        if value > current_year:
            raise serializers.ValidationError(
                f"Год не может быть больше текущего года ({current_year})."
            )
        return value

    def validate(self, attr):  # noqa: C901
        if 'genre' not in self.initial_data:
            raise ValidationError(
                'Отсутствует обязательный параментр genre'
            )
        genre_slugs = self.initial_data.get('genre')
        if not isinstance(genre_slugs, list):
            raise ValidationError(
                'Параментр genre должен быть списком'
            )
        if not len(genre_slugs):
            raise ValidationError(
                'Параментр genre не должен быть пустым'
            )
        try:
            for genre_slug in genre_slugs:
                _ = Genre.objects.get(slug=genre_slug)
        except Genre.DoesNotExist:
            raise ValidationError(
                f'Жанра {genre_slug} не существует'
            )

        if 'category' not in self.initial_data:
            raise ValidationError(
                'Отсутствует обязательный параментр category'
            )
        category_slug = self.initial_data.get('category')
        if not isinstance(category_slug, str):
            raise ValidationError(
                'Параментр category должен быть строкой'
            )
        try:
            _ = Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            raise ValidationError(
                f'Категории {category_slug} не существует'
            )

        return super().validate(attr)

    def create(self, validated_data):
        category = Category.objects.get(
            slug=self.initial_data.get('category')
        )
        title = Title.objects.create(**validated_data, category=category)

        genre_slugs = self.initial_data.get('genre')
        self.__save_genres(title, genre_slugs)
        return title

    def update(self, instance, validated_data):
        category = Category.objects.get(
            slug=self.initial_data.get('category')
        )
        genre_slugs = self.initial_data.get('genre')
        GenreTitle.objects.filter(title=instance).delete()

        instance.name = validated_data.get('name', instance.name)
        instance.year = validated_data.get('year', instance.year)
        instance.description = validated_data.get(
            'description', instance.description
        )
        instance.category = category
        instance.save()
        self.__save_genres(instance, genre_slugs)
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

    def __save_genres(self, title, genre_slugs):
        for genre_slug in genre_slugs:
            genre = Genre.objects.get(slug=genre_slug)
            GenreTitle.objects.create(
                genre=genre,
                title=title
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
            pk=self.context['view'].kwargs['title_id']
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
            'score',
            'pub_date'
        )
        read_only_fields = (
            'id',
            'author',
            'title',
            'pub_date'
        )


class UsernameEmailSreializer(serializers.Serializer):
    """Сериализатор для username."""

    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=150,
        required=True,
    )

    def validate_username(self, value):
        if value == 'me':
            raise ValidationError('Использовать имя me запрещено.')
        return value

    email = serializers.EmailField(required=True, max_length=254)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для логики /users/."""

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
        fields = [
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        ]


class UserMeSerializer(UserSerializer):
    """Сериализатор для логики эндпоинта /me/ ."""

    role = serializers.CharField(read_only=True)


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
