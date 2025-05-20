from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models


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

    def validate_username_me(self, value):
        if value == 'me':
            raise ValidationError('Имя "me" запрещено')

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator, validate_username_me]
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
    
    def validate_username_me(self, value):
        if value == 'me':
            raise ValidationError('Имя "me" запрещено')
