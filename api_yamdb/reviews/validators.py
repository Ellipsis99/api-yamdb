from django.conf import settings
from django.core.exceptions import ValidationError

from .utils import current_year


def year_validator(value):
    if value < 0:
        raise ValidationError('Год выпуска не может быть отрицательным!')
    if value > current_year():
        raise ValidationError('Год выпуска не может быть больше текущего!')


def score_validator(value):
    if value < settings.MIN_SCORE:
        raise ValidationError(
            f'Оценка не может быть ниже {settings.MIN_SCORE}.'
        )
    if value > settings.MAX_SCORE:
        raise ValidationError(
            f'Оценка не может быть выше {settings.MAX_SCORE}.'
        )
