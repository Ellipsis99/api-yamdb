from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from reviews.models import Review, Title

from .permissions import IsAuthorModeratorAdminOrReadOnly
from .serializers import CommentSerializer, ReviewSerializer


# === Зона dev3 (моя): отзывы и комментарии ===
# Title — заглушка из reviews.models (полную модель/API делает dev2).
class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для отзывов, вложенных в произведение."""

    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly, IsAuthorModeratorAdminOrReadOnly
    )
    pagination_class = PageNumberPagination
    http_method_names = ('get', 'post', 'patch', 'delete')

    def _get_title(self):
        """Возвращает произведение по id из URL."""
        return get_object_or_404(Title, pk=self.kwargs['title_id'])

    def get_queryset(self):
        """Возвращает отзывы указанного произведения."""
        return self._get_title().reviews.all()

    def perform_create(self, serializer):
        """Создаёт отзыв от имени текущего пользователя."""
        serializer.save(author=self.request.user, title=self._get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для комментариев, вложенных в отзыв."""

    serializer_class = CommentSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly, IsAuthorModeratorAdminOrReadOnly
    )
    pagination_class = PageNumberPagination
    http_method_names = ('get', 'post', 'patch', 'delete')

    def _get_review(self):
        """Возвращает отзыв по id из URL в рамках нужного произведения."""
        return get_object_or_404(
            Review,
            pk=self.kwargs['review_id'],
            title_id=self.kwargs['title_id'],
        )

    def get_queryset(self):
        """Возвращает комментарии указанного отзыва."""
        return self._get_review().comments.all()

    def perform_create(self, serializer):
        """Создаёт комментарий от имени текущего пользователя."""
        serializer.save(author=self.request.user, review=self._get_review())
