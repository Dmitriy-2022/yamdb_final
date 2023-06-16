import datetime

from django.conf import settings
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .mixins import MeValidator
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class CategorySerializer(serializers.ModelSerializer):
    """"Сериализатор для работы с категориями"""

    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    """"Сериализатор для работы с жанрами"""

    class Meta:
        model = Genre
        exclude = ('id',)


class TitleListRetrieveSerializer(serializers.ModelSerializer):
    """"Сериализатор для работы со списком произведений"""
    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.IntegerField(default=None)

    class Meta:
        model = Title
        fields = (
            'id', 'name',
            'year', 'description',
            'category', 'genre', 'rating',
        )
        read_only_fields = (
            'id', 'name', 'year', 'description', 'category', 'genre', 'rating',
        )


class TitleSerializer(serializers.ModelSerializer):
    """"Сериализатор для работы произведенями"""
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        slug_field='slug'
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'category', 'genre')

    def validate_year(self, value):
        if value > datetime.datetime.now().year:
            raise serializers.ValidationError(
                f'Год выпуска {value} больше текущего'
            )
        return value

    def to_representation(self, value):
        return TitleListRetrieveSerializer(value).data


class ReviewSerializer(serializers.ModelSerializer):
    """"Сериализатор для работы с оценками"""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    score = serializers.IntegerField(
        validators=[MinValueValidator(1,
                    message='Оценка не может быть меньше 1'),
                    MaxValueValidator(10,
                    message='Оценка не может быть больше 10')],
        default=5
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('title',)

    def validate(self, data):
        if (self.context['request'].method == 'POST' and Review.objects.filter(
                author=self.context['request'].user,
                title=self.context['request'].parser_context['kwargs'][
                    'title_id'])):
            raise serializers.ValidationError(
                'На одно произведение можно оставить лишь один отзыв!')
        return data


class CommentSerializer(serializers.ModelSerializer):
    """"Сериализатор для работы с комментариями"""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('review',)


class UsersSerializer(serializers.ModelSerializer):
    """"Сериализатор для работы с пользователями"""
    username = serializers.CharField(
        max_length=settings.USERNAME_MAX_LENGTH,
        validators=[
            UnicodeUsernameValidator(),
            UniqueValidator(queryset=User.objects.all())],
    )
    email = serializers.EmailField(
        required=True,
        max_length=settings.EMAIL_MAX_LENGTH,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'username', 'email',
            'first_name', 'last_name',
            'bio', 'role',
        )


class SignUpSerializer(serializers.ModelSerializer, MeValidator):
    """"Сериализатор для работы авторизацией"""
    username = serializers.CharField(
        required=True,
        max_length=settings.USERNAME_MAX_LENGTH,
    )
    email = serializers.EmailField(
        required=True,
        max_length=settings.EMAIL_MAX_LENGTH,
    )

    class Meta:
        model = User
        fields = ('username', 'email')


class GetTokenSerializer(serializers.Serializer, MeValidator):
    """"Сериализатор для работы с токенами"""
    confirmation_code = serializers.CharField(required=False)
    username = serializers.CharField(
        required=True,
    )
