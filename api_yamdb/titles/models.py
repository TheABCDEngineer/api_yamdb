from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator

User = get_user_model()


class Category(models.Model):
    name = models.TextField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(models.Model):
    name = models.TextField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.TextField(max_length=256)
    year = models.IntegerField()
    description = models.TextField(blank=True)
    genre = models.ManyToManyField(Genre, related_name='titles')
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="titles",
        blank=False,
        null=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'


class Review(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.IntegerField(
        verbose_name='Оценка',
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10)
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='only_one_review_to_title'
            )
        ]


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
