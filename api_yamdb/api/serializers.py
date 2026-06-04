from rest_framework import serializers

from reviews.models import Category, Genre, Title
from reviews.utils import current_year


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
