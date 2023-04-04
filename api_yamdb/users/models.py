import re

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework import serializers


def validate_username(value):
    USERNAME_ME = 'Нельзя использовать "me" в качестве username'
    USERNAME_EMPTY = 'Поле "username" не должно быть пустым'
    if value == 'me' or '':
        invalid_username = USERNAME_ME if (
            value == 'me') else USERNAME_EMPTY
        raise serializers.ValidationError(detail=[invalid_username])
    result = re.findall(r'[^\w.@+-]', value)
    if result:
        raise serializers.ValidationError(
            f'Некорректные символы в username:'
            f' `{"`, `".join(set(result))}`.'
        )
    return value


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLES = (
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Пользователь'),
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=settings.EMAIL_MAX_LENGTH,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=settings.USERNAME_MAX_LENGTH,
        validators=[validate_username],
        unique=True,
    )
    role = models.CharField(
        'Роль', max_length=max([len(value) for value, name in ROLES]),
        choices=ROLES, default='user',
    )
    bio = models.TextField(
        'Биография',
        null=True,
        blank=True
    )
    first_name = models.TextField(
        'Имя',
        max_length=settings.USER_NAME_MAX_LENGTH,
        null=True,
        blank=True
    )
    last_name = models.TextField(
        'Фамилия',
        max_length=settings.USER_NAME_MAX_LENGTH,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return (
            self.role == self.ADMIN
            or self.is_superuser
            or self.is_staff
        )
