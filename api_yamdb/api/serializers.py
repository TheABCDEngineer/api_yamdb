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


class TitleGet(serializers.ModelSerializer):
    category = CategorySerializer(many=False, read_only=True)
    genre = GenreSerializer(many=True, required=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = "__all__"


class TitlePost(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'

    def validate_name(self, value):
        if len(value) > 256:
            raise serializers.ValidationError(
                "Длинна названия не должна превышать 256 символов."
            )
        return value

    def validate_year(self, value):
        current_year = datetime.date.today().year
        if value > current_year:
            raise serializers.ValidationError(
                f"Год не может быть больше текущего года ({current_year})."
            )
        return value

    def create(self, validated_data):
        genres_data = validated_data.pop('genre')
        category_obj = validated_data.pop('category')
        title = Title.objects.create(**validated_data, category=category_obj)
        title.genre.set(genres_data)
        return title

    def update(self, instance, validated_data):
        if 'genre' in validated_data:
            genres_data = validated_data.pop('genre')
            instance.genre.clear()
            instance.genre.add(*genres_data)
        if 'category' in validated_data:
            instance.category = validated_data.pop('category')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def get_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews.exists():
            return None

        summary_score = sum(review.score for review in reviews)
        average_rating = round(summary_score / reviews.count())
        return average_rating


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
            'score',
            'pub_date',
        )
        read_only_fields = (
            'id',
            'author',
            'title',
            'pub_date',
        )


class UsernameSreializer(serializers.Serializer):
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


class SignUpSerializer(UsernameSreializer):
    """Сериализатор для логики /signup/."""
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
