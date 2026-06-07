import random
import string
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


def generate_confirmation_code(length=6):
    """Генерирует код подтверждения из цифр и букв"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def send_confirmation_email(email, code):
    """Отправляет письмо с кодом (в деве — в консоль)"""
    subject = 'Код подтверждения для YaMDB'
    message = f'Ваш код подтверждения: {code}'
    from_email = settings.DEFAULT_FROM_EMAIL

    send_mail(
        subject,
        message,
        from_email,
        [email],
        fail_silently=False
    )


def get_tokens_for_user(user):
    """Возвращает JWT-токен для пользователя"""
    refresh = RefreshToken.for_user(user)
    return {'token': str(refresh.access_token)}
