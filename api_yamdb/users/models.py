from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Пользователь YaMDb.

    Заглушка-«контракт» для параллельной работы: задаёт роль и поля,
    на которые опираются отзывы, комментарии и права доступа. Полный
    auth-флоу (регистрация, токены, подтверждение по e-mail) дописывается
    отдельно и эту модель не меняет.
    """

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLE_CHOICES = (
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    )

    email = models.EmailField('email', max_length=254, unique=True)
    role = models.CharField(
        'роль', max_length=20, choices=ROLE_CHOICES, default=USER
    )
    bio = models.TextField('биография', blank=True)

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser or self.is_staff

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    def __str__(self):
        return self.username
