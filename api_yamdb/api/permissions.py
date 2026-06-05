from rest_framework import permissions


# dev3 (моя): права на отзывы и комментарии.
# IsAdminOrReadOnly для произведений/категорий/жанров — зона dev2.
class IsAuthorModeratorAdminOrReadOnly(permissions.BasePermission):
    """Чтение — всем; запись автору, модератору или администратору."""

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
