from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


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

# https://stackoverflow.com/questions/18676156/how-to-properly-use-the-choices-field-option-in-django
# Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.
# https://stackoverflow.com/questions/36409257/required-30-characters-or-fewer-letters-digits-and-only


class User(AbstractUser):
    """Модель User."""

    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLE_CHOIСES = (
        (ADMIN, 'Админинстратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Обычный пользователь'),
    )

    username_validator = RegexValidator(
        regex=r'^[\w.@+-]+$',
        message=('Имя пользователя должно содержать только'
                 ' буквы, цифры и символы @/./+/-/_'),
        code='invalid_username'
    )

    bio = models.TextField(
        blank=True,
        verbose_name='Биография'
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOIСES,
        default=USER,
        verbose_name='Роль пользователя'
    )

    confirmation_code = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username
