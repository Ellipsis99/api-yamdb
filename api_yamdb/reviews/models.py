from django.contrib.auth import get_user_model
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models

from .utils import current_year

User = get_user_model()

MIN_SCORE = 1
MAX_SCORE = 10


# === Зона dev2: произведения, категории, жанры ===
# (подняла как фундамент под отзывы; основа — ветка feature/titles-part)
class Genre(models.Model):
    """Жанр произведения."""

    name = models.CharField('название', max_length=256)
    slug = models.SlugField('слаг', max_length=50, unique=True)

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(models.Model):
    """Категория произведения."""

    name = models.CharField('название', max_length=256)
    slug = models.SlugField('слаг', max_length=50, unique=True)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Title(models.Model):
    """Произведение, на которое пишут отзывы."""

    name = models.CharField('название', max_length=256)
    year = models.IntegerField(
        'год выпуска',
        validators=[
            MinValueValidator(
                0, message='Год выпуска не может быть отрицательным!'
            ),
            MaxValueValidator(
                current_year,
                message='Год выпуска не может быть больше текущего!',
            ),
        ],
    )
    description = models.TextField('описание', null=True, blank=True)
    genre = models.ManyToManyField(
        Genre, through='GenreTitle', related_name='titles'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='titles',
    )

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Связь произведения и жанра."""

    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['genre', 'title'], name='unique_genre_title'
            )
        ]


# === Зона dev3 (моя): отзывы и комментарии ===
class Review(models.Model):
    """Отзыв пользователя на произведение."""

    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews'
    )
    text = models.TextField('текст')
    score = models.PositiveSmallIntegerField(
        'оценка',
        validators=[
            MinValueValidator(
                MIN_SCORE, message=f'Оценка не может быть ниже {MIN_SCORE}.'
            ),
            MaxValueValidator(
                MAX_SCORE, message=f'Оценка не может быть выше {MAX_SCORE}.'
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
        Review, on_delete=models.CASCADE, related_name='comments'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments'
    )
    text = models.TextField('текст')
    pub_date = models.DateTimeField('дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text
