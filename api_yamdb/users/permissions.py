from rest_framework import permissions


class IsAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Сначала проверяем, что пользователь аутентифицирован
        if not request.user or request.user.is_anonymous:
            return False
        return request.user.is_admin
    