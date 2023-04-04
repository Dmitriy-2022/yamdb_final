import csv

from django.core.management.base import BaseCommand

from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title
from users.models import User


class Command(BaseCommand):
    help = 'Загрузка данных из .csv файлов'

    def _load_user(self):
        with open(
                'static/data/users.csv',
                encoding='utf-8'
        ) as csvfile:
            reader = csv.DictReader(csvfile)
            object_list = []
            for row in reader:
                object_list.append(User(**row))
            User.objects.bulk_create(objs=object_list)
        self.stdout.write('Data for the User table is loaded!')

    def _load_category(self):
        with open(
                'static/data/category.csv',
                encoding='utf-8'
        ) as csvfile:
            reader = csv.DictReader(csvfile)
            object_list = []
            for row in reader:
                object_list.append(Category(**row))
            Category.objects.bulk_create(objs=object_list)
        self.stdout.write('Data for the Category table is loaded!')

    def _load_genre(self):
        with open(
                'static/data/genre.csv',
                encoding='utf-8'
        ) as csvfile:
            reader = csv.DictReader(csvfile)
            object_list = []
            for row in reader:
                object_list.append(Genre(**row))
            Genre.objects.bulk_create(objs=object_list)
        self.stdout.write('Data for the Genre table is loaded!')

    def _load_title(self):
        with open(
                'static/data/titles.csv',
                encoding='utf-8'
        ) as csvfile:
            reader = csv.DictReader(csvfile)
            object_list = []
            for row in reader:
                object_list.append(Title(
                    pk=row['id'],
                    name=row['name'],
                    year=row['year'],
                    category=Category.objects.get(pk=row['category']),
                ))
            Title.objects.bulk_create(objs=object_list)
        self.stdout.write('Data for the Title table is loaded!')

    def _load_genretitle(self):
        with open(
                'static/data/genre_title.csv',
                encoding='utf-8'
        ) as csvfile:
            reader = csv.DictReader(csvfile)
            object_list = []
            for row in reader:
                object_list.append(GenreTitle(
                    pk=row['id'],
                    genre=Genre.objects.get(pk=row['genre_id']),
                    title=Title.objects.get(pk=row['title_id']),
                ))
            GenreTitle.objects.bulk_create(objs=object_list)
        self.stdout.write('Data for the GenreTitle table is loaded!')

    def _load_review(self):
        with open(
                'static/data/review.csv',
                encoding='utf-8'
        ) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data = Review(
                    pk=row['id'],
                    title=Title.objects.get(pk=row['title_id']),
                    text=row['text'],
                    author=User.objects.get(pk=row['author']),
                    score=row['score'],
                    pub_date=row['pub_date'],
                )
                data.save()
                Review.objects.filter(
                    pk=row['id']).update(pub_date=row['pub_date']
                                         )
        self.stdout.write('Data for the Review table is loaded!')

    def _load_comment(self):
        with open(
                'static/data/comments.csv',
                encoding='utf-8'
        ) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data = Comment(
                    pk=row['id'],
                    review=Review.objects.get(pk=row['review_id']),
                    text=row['text'],
                    author=User.objects.get(pk=row['author']),
                    pub_date=row['pub_date'],
                )
                data.save()
                Comment.objects.filter(
                    pk=row['id']).update(pub_date=row['pub_date']
                                         )
        self.stdout.write('Data for the Comment table is loaded!')

    def handle(self, *args, **options):
        self._load_user()
        self._load_category()
        self._load_genre()
        self._load_title()
        self._load_genretitle()
        self._load_review()
        self._load_comment()
