from rest_framework import permissions


# class IsAdminOrReadOnly(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return (
#             request.method in permissions.SAFE_METHODS or request.user.is_admin
#         )


class IsEditOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # fix: была опечатка и без проверки админа
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        )

    def has_object_permission(self, request, view, obj):
        # fix: убрал проверку obj.author т.к у произведений нет автора —
        # изменять/удалять может администратор
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        )


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


class IsAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Сначала проверяем, что пользователь аутентифицирован
        if not request.user or request.user.is_anonymous:
            return False
        return request.user.is_admin
