from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Category, Comment, Genre, GenreTitle, Review, Title, User


admin.site.empty_value_display = 'Не задано'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'author',
        'score', 'pub_date'
    )
    list_filter = (
        'score', 'pub_date'
    )
    search_fields = ('text', 'author__username')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'review', 'author', 'pub_date')
    list_filter = ('pub_date',)
    search_fields = ('text', 'author__username')


@admin.register(Category, Genre)
class PropertyTitleAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'slug'
    )
    list_editable = (
        'name', 'slug'
    )
    search_fields = ('slug', 'name')


class GenreTitleInline(admin.StackedInline):
    model = GenreTitle
    autocomplete_fields = ('genre', 'title')
    extra = 1


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    inlines = (GenreTitleInline,)
    list_display = (
        'id', 'name', 'year',
        'description', 'category'
    )
    list_editable = (
        'name', 'year', 'description', 'category'
    )
    search_fields = ('name',)


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
