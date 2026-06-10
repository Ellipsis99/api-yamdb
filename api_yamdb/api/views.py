from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters,
    mixins,
    permissions,
    response,
    status,
    viewsets
)
from rest_framework.decorators import action

from reviews.models import Category, Genre, Review, Title
from reviews.utils import get_tokens_for_user

from .filters import TitleFilter
from .permissions import (
    IsAdminOnly,
    IsAuthorModeratorAdminOrReadOnly,
    IsEditOrReadOnly,
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    MeSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleDetailSerializer,
    TitleSerializer,
    TokenSerializer,
    UserSerializer,
)

User = get_user_model()


class AuthViewSet(viewsets.GenericViewSet):
    """ViewSet для обработки аутентификации и получения токена."""

    permission_classes = (permissions.AllowAny,)

    @action(methods=['POST'], detail=False, url_path='signup')
    def signup(self, request, *args, **kwargs):
        """Регистрация нового пользователя и отправка кода подтверждения."""
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='token')
    def token(self, request, *args, **kwargs):
        """Получение JWT-токена по username и confirmation_code."""
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        tokens = get_tokens_for_user(user)
        return response.Response(tokens, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для управление пользователями (только для администратора)."""

    queryset = User.objects.all()
    lookup_field = 'username'
    serializer_class = UserSerializer
    permission_classes = [IsAdminOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']

    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    def get_serializer_class(self):
        """Возвращает MeSerializer для эндпоинта /me/, иначе UserSerializer."""
        if self.action == 'me':
            return MeSerializer
        return UserSerializer

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        url_path='me',
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request, *args, **kwargs):
        """Получение и частичное обновление профиля текущего пользователя."""
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return response.Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        """Запрещает пользователю удалять самого себя."""
        if instance == self.request.user:
            raise permissions.PermissionDenied('Нельзя удалить самого себя.')
        instance.delete()


class PropertyTitleViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Базовый ViewSet для свойств произведения."""

    permission_classes = (IsEditOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(PropertyTitleViewSet):
    """ViewSet для жанров произведения."""

    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer


class CategoryViewSet(PropertyTitleViewSet):
    """ViewSet для категории произведения."""

    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для произведений."""

    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('name')
    permission_classes = (IsEditOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    lookup_url_kwarg = 'titles_id'

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return TitleSerializer
        return TitleDetailSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для отзывов, вложенных в произведение."""

    serializer_class = ReviewSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsAuthorModeratorAdminOrReadOnly
    )
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
        permissions.IsAuthenticatedOrReadOnly, IsAuthorModeratorAdminOrReadOnly
    )
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
