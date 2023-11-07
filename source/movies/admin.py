from django.contrib import admin

from .models import Filmwork, Genre, GenreFilmwork, Person, PersonFilmwork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description',
    )
    search_fields = ('name',)


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline, PersonFilmworkInline)

    list_display = (
        'title',
        'type',
        'creation_date',
        'rating',
    )
    list_filter = (
        'type',
        'rating',
    )
    search_fields = ('title', 'description', 'id')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('genres').prefetch_related('persons')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name',)
    search_fields = ('full_name',)
