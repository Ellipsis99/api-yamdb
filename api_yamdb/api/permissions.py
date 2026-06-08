from rest_framework import permissions


class IsEditOrReadOnly(permissions.BasePermission):
    """Доступ к изменению контента."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        )

    def has_object_permission(self, request, view, obj):
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

    def has_permission(self, request, view):
        if not request.user or request.user.is_anonymous:
            return False
        return request.user.is_admin
