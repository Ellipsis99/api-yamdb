from django.utils import timezone


def current_year():
    """Возвращает текущий год — верхняя граница для года выпуска."""
    return timezone.now().year
