from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import OuterRef, Q, Subquery
from django.db.models.query import QuerySet
from django.http import JsonResponse
from django.views.generic.base import View
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from movies.models import Filmwork, PersonFilmwork


class MoviesApiMixin(View):
    model = Filmwork
    http_method_names = ['get']

    def get_queryset(self) -> QuerySet:
        """
        Возвращает подготовленный Queryset в соответствии с запросом.
        """
        if record_id := self.kwargs.get('pk', None):
            query_set = self.model.objects.filter(id=record_id)
        else:
            query_set = self.model.objects

        return (
            query_set.values()
            .prefetch_related('genres', 'persons')
            .annotate(
                genres=self.get_genres_subquery(),
                actors=self.get_persons_subquery(
                    PersonFilmwork.PersonFilmworkRoles.ACTOR
                ),
                directors=self.get_persons_subquery(
                    PersonFilmwork.PersonFilmworkRoles.DIRECTOR
                ),
                writers=self.get_persons_subquery(
                    PersonFilmwork.PersonFilmworkRoles.WRITER
                ),
            )
        )

    def get_genres_subquery(self) -> Subquery:
        """
        Возвращает объект класса Subquery c колонкой genres_.
        Каждая запись в колонке содержит жанры для фильма из таблицы Filmwork.
        """
        genres = (
            self.model.objects.prefetch_related('genres')
            .annotate(genres_=ArrayAgg('genres__name'))
            .filter(pk=OuterRef('pk'))
        )
        return Subquery(genres.values('genres_'))

    def get_persons_subquery(
        self, role: PersonFilmwork.PersonFilmworkRoles
    ) -> Subquery:
        """
        Возвращает объект класса Subquery c колонкой genres_.
        Каждая запись в колонке содержит жанры для фильма из таблицы Filmwork.
        """
        persons = (
            self.model.objects.prefetch_related('persons')
            .annotate(
                roles=ArrayAgg(
                    'persons__full_name',
                    filter=Q(personfilmwork__role=role),
                )
            )
            .filter(pk=OuterRef('pk'))
        )

        return Subquery(persons.values('roles'))

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    def get_context_data(self, *, object_list=None, **kwargs):
        context = {
            'results': list(self.get_queryset()),
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    def get_context_data(self, *, object_list=None, **kwargs):
        context = {
            'results': list(self.get_queryset()),
        }
        return context
