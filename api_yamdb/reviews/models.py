from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.db import models

from reviews.validators import validate_year
from users.models import User


class ReviewCommentBaseModel(models.Model):
    text = models.TextField(
        'Текст',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True
        ordering = ('pub_date',)

    def __str__(self):
        return self.text[:30]


class CategoryGenreBaseModel(models.Model):
    name = models.CharField(
        'Наименование', max_length=settings.NAME_MAX_LENGTH
    )
    slug = models.SlugField(unique=True, max_length=settings.SLUG_MAX_LENGTH)

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name[:20]


class Genre(CategoryGenreBaseModel):
    class Meta(CategoryGenreBaseModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Category(CategoryGenreBaseModel):
    class Meta(CategoryGenreBaseModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Title(models.Model):
    name = models.CharField(
        'Произведение', max_length=settings.NAME_MAX_LENGTH
    )
    year = models.PositiveSmallIntegerField(
        'Год выпуска',
        validators=[validate_year],
        db_index=True,
    )
    description = models.TextField(
        'Описание',
        null=True,
        blank=True
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        related_name='categories',
        null=True,
        blank=True,
    )
    genre = models.ManyToManyField(Genre, through='GenreTitle')

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self):
        return self.name[:30]


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
    )
    genre = models.ForeignKey(
        Genre,
        verbose_name='Жанр',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Произведение и жанр'
        verbose_name_plural = 'Произведения и жанры'
        ordering = ('id',)

    def __str__(self):
        return (
            f'Произведение:{self.title[:30]},'
            f'\nЖанр:{self.genre[:30]}'
        )


class Review(ReviewCommentBaseModel):
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=[MinValueValidator(1,
                    message='Оценка не может быть меньше 1'),
                    MaxValueValidator(10,
                    message='Оценка не может быть больше 10')],
        default=5
    )
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
    )

    class Meta(ReviewCommentBaseModel.Meta):
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = 'reviews'
        constraints = [
            models.UniqueConstraint(fields=['title', 'author'],
                                    name='unique_review')
        ]


class Comment(ReviewCommentBaseModel):
    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE,
    )

    class Meta(ReviewCommentBaseModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
