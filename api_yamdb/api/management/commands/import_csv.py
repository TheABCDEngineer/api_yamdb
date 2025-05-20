from django.core.management.base import BaseCommand
import csv
import os
from django.conf import settings
from reviews.models import Category, Genre, Title


class Command(BaseCommand):
    help = 'Импорт данных из CSV файлов'

    def handle(self, *args, **kwargs):
        data_dir = os.path.join(settings.BASE_DIR, 'static', 'data')

        with open(os.path.join(data_dir, 'category.csv'), encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Category.objects.update_or_create(
                    slug=row['slug'],
                    defaults={'name': row['name']}
                )

        with open(os.path.join(data_dir, 'genre.csv'), encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Genre.objects.update_or_create(
                    slug=row['slug'],
                    defaults={'name': row['name']}
                )

        with open(os.path.join(data_dir, 'titles.csv'), encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                category = Category.objects.filter(id=int(row['category'])).first()
                Title.objects.update_or_create(
                    id=int(row['id']),
                    defaults={
                        'name': row['name'],
                        'year': int(row['year']),
                        'description': '',
                        'category': category
                    }
                )

        with open(os.path.join(data_dir, 'genre_title.csv'), encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = Title.objects.filter(id=int(row['title_id'])).first()
                genre = Genre.objects.filter(id=int(row['genre_id'])).first()
                if title and genre:
                    title.genre.add(genre)

        self.stdout.write(self.style.SUCCESS('Данные успешно импортированы'))
