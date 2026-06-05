from django.contrib.auth import get_user_model
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.db.models import Avg

User = get_user_model()

MIN_SCORE = 1
MAX_SCORE = 10


# === Заглушка зоны dev2 ===
# Произведения/категории/жанры и их API — задача dev2, на develop их нет.
# Здесь оставлена МИНИМАЛЬНАЯ модель Title как контракт: на неё ссылается
# Review (FK) и считается рейтинг. dev2 заменит её полной версией
# (year, description, genre M2M, category FK) и добавит API.
class Title(models.Model):
    """Произведение (заглушка). Полную версию делает dev2."""

    name = models.CharField('название', max_length=256)

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self):
        return self.name

    # dev3 (моя): рейтинг — средняя оценка по отзывам
    @property
    def rating(self):
        return self.reviews.aggregate(Avg('score'))['score__avg']


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
