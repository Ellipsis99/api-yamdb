from rest_framework import serializers

from reviews.models import Comment, Review


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
