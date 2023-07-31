from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from foodgram.settings import NAME_MAX_LENGTH, USER_EMAIL_MAX_LENGTH


class CustomUser(AbstractUser):
    """Модель пользователей."""
    email = models.EmailField(
        max_length=USER_EMAIL_MAX_LENGTH,
        unique=True,
        verbose_name='Электронная почта пользователя'
    )
    username = models.CharField(
        max_length=NAME_MAX_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                r'^[\w.@+-]+\Z',
                message='Никнейм должен содержать: буквы латинского алфавита,'
                'цифры, подчеркивание, знак "@"'
            ),
        ],
        verbose_name='Никнейм пользователя'
    )
    first_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name='Имя пользователя'
    )
    last_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name='Фамилия пользователя'
    )
    password = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name='Пароль'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    def __str__(self):
        return f'{self.username} - {self.email}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['email', 'password'],
                name='unique_password_email'
            )
        ]


class Subscription(models.Model):
    """Модель подписки."""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписчик'
    )
    following = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Подписки'
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки',
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following'
            )
        ]
