from django.core.exceptions import ValidationError

from .utils import current_year


def year_validator(value):
    if value < 0:
        raise ValidationError('Год выпуска не может быть отрицательным!')
    if value > current_year():
        raise ValidationError('Год выпуска не может быть больше текущего!')
