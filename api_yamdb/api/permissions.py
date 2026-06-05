from rest_framework import permissions


# === Зона dev2: права на произведения/категории/жанры ===
class IsEditOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # fix: было `SAFE_METHOD` (опечатка) и без проверки админа —
        # из-за этого запись не работала вообще
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        )

    def has_object_permission(self, request, view, obj):
        # fix: убрана проверка obj.author (у произведений нет автора) —
        # изменять/удалять может администратор
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        )


# === Зона dev3 (моя): права на отзывы и комментарии ===
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
