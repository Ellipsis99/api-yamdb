from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title
from reviews.utils import current_year


# === Зона dev2: сериализаторы произведений/категорий/жанров (как есть) ===
class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class BaseTitleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def validate_year(self, value):
        cur_year = current_year()
        if value > cur_year:
            raise serializers.ValidationError('Проверьте год выпуска!')
        return value


class TitleDetailSerializer(BaseTitleSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    # dev3 (моя): рейтинг — средняя оценка по отзывам
    rating = serializers.IntegerField(read_only=True, default=None)

    class Meta(BaseTitleSerializer.Meta):
        # dev3: добавлено поле rating в выдачу произведения
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class TitleSerializer(BaseTitleSerializer):
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    def to_representation(self, instance):
        return TitleDetailSerializer(instance).data


# === Зона dev3 (моя): сериализаторы отзывов и комментариев ===
class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзывов."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, attrs):
        request = self.context['request']
        if request.method != 'POST':
            return attrs
        title_id = self.context['view'].kwargs['title_id']
        if Review.objects.filter(
            title_id=title_id, author=request.user
        ).exists():
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на это произведение.'
            )
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментариев к отзыву."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
