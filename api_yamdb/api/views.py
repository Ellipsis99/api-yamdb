from rest_framework import viewsets, filters, mixins
from django_filters.rest_framework import DjangoFilterBackend

from reviews.models import Genre, Title, Category
from .permissions import IsAdminOrReadOnly
from .serializers import (
    GenreSerializer,
    CategorySerializer,
    TitleSerializer,
    TitleDetailSerializer
)


class PropertyViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly, )
    lookup_field = 'slug'


class GenreViewSet(PropertyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(PropertyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    http_method_names = ["get", "post", "patch", "delete"]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('category__slug', 'genre__slug', 'name', 'year')
    permission_classes = (IsAdminOrReadOnly, )
    lookup_url_kwarg = 'titles_id'

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return TitleSerializer
        return TitleDetailSerializer
