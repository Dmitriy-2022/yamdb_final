from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Category, Comment, Genre, GenreTitle, Review, Title


class GenreTitleTabular(admin.TabularInline):
    model = GenreTitle


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'category', 'year', 'get_genres')
    list_filter = ('category',)
    list_editable = ('category', 'year',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'
    inlines = [GenreTitleTabular, ]

    def get_genres(self, obj):
        return ', '.join([str(genre) for genre in obj.genre.all()])
    get_genres.short_description = 'Жанры'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'score', 'title', 'author')
    list_filter = ('pub_date',)
    search_fields = ('text',)
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'review', 'author')
    list_filter = ('pub_date',)
    search_fields = ('text',)
    empty_value_display = '-пусто-'


@admin.register(GenreTitle)
class GenreTitleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'genre')


admin.site.unregister(Group)
