from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


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
    # username = models.CharField(
    #     max_length=150,
    #     unique=True,
    #     verbose_name='Имя пользователя'
    # )

    # email = models.EmailField(
    #     max_length=254,
    #     unique=True,
    #     verbose_name='Электронная почта'
    # )
    # first_name = models.CharField(
    #     max_length=150,
    #     blank=True,
    #     verbose_name='Имя'
    # )
    # last_name = models.CharField(
    #     max_length=150,
    #     blank=True,
    #     verbose_name='Фамилия'
    # )
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
