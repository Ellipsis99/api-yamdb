from .permissions import IsAdminOrReadOnly #пермишен
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from reviews.models import Category, Genre, Review, Title

from .permissions import (
    IsAuthorModeratorAdminOrReadOnly,
    IsEditOrReadOnly,
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleDetailSerializer,
    TitleSerializer,
)


class PropertyViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    # fix: добавил права (write — только админ) и lookup по slug
    permission_classes = (IsEditOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(PropertyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(PropertyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(viewsets.ModelViewSet): ##пермишен
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('name')
    permission_classes = (IsEditOrReadOnly,)  # fix: write — только админ
    http_method_names = ["get", "post", "patch", "delete"]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('category__slug', 'genre__slug', 'name', 'year')
    lookup_url_kwarg = 'titles_id'
    # Аннотация рейтинга (Avg по отзывам) + сортировка
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('name')
    permission_classes = (IsEditOrReadOnly,)  # fix: write — только админ


    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return TitleSerializer
        return TitleDetailSerializer


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
