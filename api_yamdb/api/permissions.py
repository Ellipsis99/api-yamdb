from rest_framework import permissions


class IsEditOrReadOnly(permissions.BasePermission):
    """Доступ к изменению контента."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        )


class IsAuthorModeratorAdminOrReadOnly(permissions.BasePermission):
    """Чтение — всем, запись - автору, модератору или администратору."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )


class IsAdminOnly(permissions.BasePermission):
    """Доступ только для администратора."""
    # кажется именно этого хочет ревьюер. 
    # вместо or поизтивный and + едионообразие с остальным кодом.
    # без is_authenticated будут пробелмы с анонимами,
    # по этому проверяем авторизацию и уточняеем что это админ.
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin