from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Category, Comment, Genre, GenreTitle, Review, Title, User

## (необязательный) Можно улучшить админку - добавить 
# вывод полей в списки, фильтрацию и т.д. https://docs.djangoproject.com/en/5.0/ref/contrib/admin/
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Title)
admin.site.register(GenreTitle)
admin.site.register(Review)
admin.site.register(Comment)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Регистрация модели пользователя."""

    list_display = (
        'username', 'email', 'first_name',
        'last_name', 'role', 'is_active'
    )
    list_filter = ('role', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Персональные данные', {
            'fields': ('first_name', 'last_name', 'bio')
        }),
        ('Права доступа', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)
