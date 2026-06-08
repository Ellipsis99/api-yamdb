import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from reviews.models import (
    Category,
    Comment,
    Genre,
    GenreTitle,
    Review,
    Title,
    User,
)


class Command(BaseCommand):
    """Загружает данные из CSV-файлов в базу данных (с очисткой БД)."""

    help = 'Загружает данные из CSV-файлов в БД (очищает БД перед загрузкой)'

    def handle(self, *args, **options):
        """Основная логика команды."""
        base_path = Path(settings.BASE_DIR) / 'static' / 'data'

        if not base_path.exists():
            self.stdout.write(
                self.style.ERROR(f'Папка не найдена: {base_path}')
            )
            return

        self._clear_database()

        self._load_data(base_path / 'category.csv', Category,
                        lambda row: Category(
                            id=int(row['id']),
                            name=row['name'],
                            slug=row['slug'],
                        ))

        self._load_data(base_path / 'genre.csv', Genre, lambda row: Genre(
            id=int(row['id']),
            name=row['name'],
            slug=row['slug'],
        ))

        self._load_data(base_path / 'users.csv', User, lambda row: User(
            id=int(row['id']),
            username=row['username'],
            email=row['email'],
            role=row.get('role', 'user'),
            bio=row.get('bio', ''),
            first_name=row.get('first_name', ''),
            last_name=row.get('last_name', ''),
        ))

        self._load_data(base_path / 'titles.csv', Title, lambda row: Title(
            id=int(row['id']),
            name=row['name'],
            year=int(row['year']),
            category_id=int(row['category']),
        ))

        self._load_data(base_path / 'genre_title.csv', GenreTitle,
                        lambda row: GenreTitle(
                            id=int(row['id']),
                            title_id=int(row['title_id']),
                            genre_id=int(row['genre_id']),
                        ))

        self._load_data(base_path / 'review.csv', Review, lambda row: Review(
            id=int(row['id']),
            title_id=int(row['title_id']),
            author_id=int(row['author']),
            text=row['text'],
            score=int(row['score']),
            pub_date=row['pub_date'],
        ))

        self._load_data(base_path / 'comments.csv', Comment,
                        lambda row: Comment(
                            id=int(row['id']),
                            review_id=int(row['review_id']),
                            author_id=int(row['author']),
                            text=row['text'],
                            pub_date=row['pub_date'],
                        ))

        self.stdout.write(self.style.SUCCESS('Все данные успешно загружены!'))

    def _clear_database(self):
        """Очищает все таблицы."""
        Comment.objects.all().delete()
        Review.objects.all().delete()
        GenreTitle.objects.all().delete()
        Title.objects.all().delete()
        User.objects.all().delete()
        Genre.objects.all().delete()
        Category.objects.all().delete()

    def _load_data(self, file_path, model, row_to_obj):
        """Универсальная загрузка данных из CSV в модель."""
        if not file_path.exists():
            self.stdout.write(
                self.style.WARNING(f'Файл не найден: {file_path}')
            )
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            objects = []
            for row in reader:
                objects.append(row_to_obj(row))
            model.objects.bulk_create(objects)
