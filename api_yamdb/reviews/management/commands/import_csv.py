import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from reviews.models import Category, Genre, Title


class Command(BaseCommand):
    help = 'Импорт данных из CSV файлов'

    def handle(self, *args, **kwargs):
        data_dir = os.path.join(settings.BASE_DIR, 'static', 'data')

        file_data = self.__get_data_from_file(data_dir, 'category.csv')
        for row in file_data:
            Category.objects.update_or_create(
                slug=row['slug'],
                defaults={'name': row['name']}
            )

        file_data = self.__get_data_from_file(data_dir, 'genre.csv')
        for row in file_data:
            Genre.objects.update_or_create(
                slug=row['slug'],
                defaults={'name': row['name']}
            )

        file_data = self.__get_data_from_file(data_dir, 'titles.csv')
        for row in file_data:
            category = Category.objects.filter(
                id=int(row['category'])
            ).first()
            Title.objects.update_or_create(
                id=int(row['id']),
                defaults={
                    'name': row['name'],
                    'year': int(row['year']),
                    'description': '',
                    'category': category
                }
            )

        file_data = self.__get_data_from_file(data_dir, 'genre_title.csv')
        for row in file_data:
            title = Title.objects.filter(id=int(row['title_id'])).first()
            genre = Genre.objects.filter(id=int(row['genre_id'])).first()
            if title and genre:
                title.genre.add(genre)

        self.stdout.write(self.style.SUCCESS('Данные успешно импортированы'))

    def __get_data_from_file(self, data_dir, file_name):
        with open(
            file=os.path.join(data_dir, file_name),
            encoding='utf-8'
        ) as file:
            data = csv.DictReader(file)
        return data
