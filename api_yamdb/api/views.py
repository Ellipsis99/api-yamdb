from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from reviews.models import Category, Genre, Review, Title

from .permissions import IsAdminOrReadOnly, IsAuthorModeratorAdminOrReadOnly
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
)


class CategoryGenreViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Базовый ViewSet для категорий и жанров: список, создание, удаление."""

    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(CategoryGenreViewSet):
    """ViewSet для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreViewSet):
    """ViewSet для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для произведений с подсчётом рейтинга по отзывам."""

    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('name')
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return TitleWriteSerializer
        return TitleReadSerializer

    def get_queryset(self):
        queryset = self.queryset
        params = self.request.query_params
        category = params.get('category')
        genre = params.get('genre')
        name = params.get('name')
        year = params.get('year')
        if category:
            queryset = queryset.filter(category__slug=category)
        if genre:
            queryset = queryset.filter(genre__slug=genre)
        if name:
            queryset = queryset.filter(name__icontains=name)
        if year:
            queryset = queryset.filter(year=year)
        return queryset


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
