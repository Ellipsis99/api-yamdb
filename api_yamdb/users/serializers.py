import random
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import NotFound

User = get_user_model()


def _send_confirmation_email(email, code):
    """Отправляет письмо с кодом подтверждения"""
    send_mail(
        subject='Код подтверждения YaMDb',
        message=f'Ваш код: {code}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(max_length=150, required=True)

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError('Имя "me" запрещено.')
        RegexValidator(regex=r'^[\w.@+-]+\Z')(value)
        return value

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')

        # Если пользователь существует — просто возвращаем данные (статус 200)
        if User.objects.filter(email=email, username=username).exists():
            return data

        # Если есть конфликт по email или username — ошибка
        if User.objects.filter(email=email).exclude(username=username).exists():
            raise serializers.ValidationError('Пользователь с таким email уже существует.')
        if User.objects.filter(username=username).exclude(email=email).exists():
            raise serializers.ValidationError('Пользователь с таким username уже существует.')

        return data

    def create(self, validated_data):
        user, created = User.objects.get_or_create(
            email=validated_data['email'],
            defaults={'username': validated_data['username']}
        )
        # Генерируем новый код подтверждения (даже если пользователь уже был)
        code = "".join([str(random.randint(0, 9)) for _ in range(6)])
        user.confirmation_code = code
        user.save()
        _send_confirmation_email(user.email, code)
        return user


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        username = data.get('username')
        code = data.get('confirmation_code')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Важно: для несуществующего пользователя — 404, а не 400
            raise NotFound('Пользователь не найден.')

        if user.confirmation_code != code:
            raise serializers.ValidationError('Неверный код подтверждения.')

        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'role')


class MeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[RegexValidator(regex=r'^[\w.@+-]+\Z', message='Некорректный username.')],
        required=False
    )
    email = serializers.EmailField(max_length=254, required=False)
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'role')
        read_only_fields = ('role',)
