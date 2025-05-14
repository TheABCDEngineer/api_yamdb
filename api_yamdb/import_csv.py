import os
import csv
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_yamdb.settings')  # замените на ваш проект
django.setup()

from api.models import Title, Category, Genre
from django.conf import settings

data_dir = os.path.join(settings.BASE_DIR, 'static/data')

for filename in os.listdir(data_dir):
    if filename.endswith('.csv'):
        filepath = os.path.join(data_dir, filename)
        with open(filepath, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if filename == 'titles.csv':
                    try:
                        category_id = int(row['category'])
                        category_obj = Category.objects.filter(id=category_id).first()
                        if not category_obj:
                            print(f"Категория с id={category_id} не найдена для {row['name']}")
                            continue
                        # Предположим, что в CSV есть колонка 'genre'
                        genre_id = int(row['genre'])
                        genre_obj = Genre.objects.filter(id=genre_id).first()
                        if not genre_obj:
                            print(f"Жанр с id={genre_id} не найден для {row['name']}")
                            continue
                        Title.objects.update_or_create(
                            name=row['name'],
                            defaults={
                                'year': int(row['year']),
                                'description': '',
                                'category': category_obj,
                                'genre': genre_obj,
                            }
                        )
                        print(f"Импортировано: {row['name']}")
                    except Exception as e:
                        print(f"Ошибка при обработке {row['name']}: {e}")
