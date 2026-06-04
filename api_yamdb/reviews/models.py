from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from .utils import current_year

class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.CharField(max_length=50, unique=True)


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.CharField(max_length=50, unique=True)


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField(
        validators=[
        MinValueValidator(0, message="Год выпуска произведения не может быть отрицательным!"),
        MaxValueValidator(current_year, message='Год выпуска произведения не может быть больше текущего!')
        ]
    )
    description = models.TextField(null=True, blank=True)
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        related_name='titles'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='titles'
    )
    


class GenreTitle(models.Model):
    genre = models.ForeignKey(
        Genre, on_delete=models.CASCADE
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['genre', 'title'], name='unique_genre_title')
        ]
