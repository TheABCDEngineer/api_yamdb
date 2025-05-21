from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import username_validator, validate_username_me


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLE_CHOIСES = (
        (ADMIN, 'Админинстратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Обычный пользователь'),
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator, validate_username_me],
        verbose_name='Имя пользователя'
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

    def __str__(self):
        return self.username
