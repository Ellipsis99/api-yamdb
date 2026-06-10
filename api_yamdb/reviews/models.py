from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models

from .validators import year_validator

class User(AbstractUser):
    """Кастомный пользователь."""

    ROLE_USER = 'user'
    ROLE_MODERATOR = 'moderator'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = [
        (ROLE_USER, 'Пользователь'),
        (ROLE_MODERATOR, 'Модератор'),
        (ROLE_ADMIN, 'Администратор'),
    ]

    email = models.EmailField(
        'Email',
        unique=True,
        max_length=254,
        db_index=True
    )
    username = models.CharField(
        'Username',
        unique=True,
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Введите корректный username'
            )
        ]
    )
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Роль',
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_USER
    )
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=100,
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.ROLE_MODERATOR or self.is_admin

    def __str__(self):
        return self.username


class PropertyTitleModel(models.Model):
    """Абстрактная модель."""

    name = models.CharField('название', max_length=256)
    slug = models.SlugField('слаг', max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Genre(PropertyTitleModel):
    """Жанр, наследник PropertyTitleModel."""

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'


class Category(PropertyTitleModel):
    """Категория, наследник PropertyTitleModel."""

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Title(models.Model):
    """Произведение."""

    name = models.CharField('название', max_length=256)
    year = models.IntegerField(
        'год выпуска',
        validators=[year_validator],
    )
    description = models.TextField('описание', null=True, blank=True)
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        related_name='titles',
        verbose_name='жанр',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='titles',
        verbose_name='категория',
    )

    class Meta: 
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Модель для связи ManyToMany."""

    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='жанр'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='произведение'
    )

    class Meta:
        verbose_name = 'связь жанра и произведения'
        verbose_name_plural = 'связи жанров и произведений'
        constraints = [
            models.UniqueConstraint(
                fields=['genre', 'title'], name='unique_genre_title'
            )
        ]


class Review(models.Model):
    """Отзыв пользователя на произведение."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='произведение',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='автор',
    )
    text = models.TextField('текст')
    score = models.PositiveSmallIntegerField(
        'оценка',
        validators=[
            MinValueValidator(
                settings.MIN_SCORE,
                message=f'Оценка не может быть ниже {settings.MIN_SCORE}.'
            ),
            MaxValueValidator(
                settings.MAX_SCORE,
                message=f'Оценка не может быть выше {settings.MAX_SCORE}.'
            ),
        ],
    )
    pub_date = models.DateTimeField('дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'], name='unique_review'
            )
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Комментарий к отзыву."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='отзыв',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор',
    )
    text = models.TextField('текст')
    pub_date = models.DateTimeField('дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text
