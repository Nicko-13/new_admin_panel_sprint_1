from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import OuterRef, Q, Subquery
from django.db.models.query import QuerySet
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from movies.models import Filmwork, PersonFilmwork


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    def get_queryset(self) -> QuerySet:
        """
        Возвращает подготовленный Queryset в соответствии с запросом.
        """
        genres = (
            self.model.objects.prefetch_related('genres')
            .annotate(genres_=ArrayAgg('genres__name'))
            .filter(pk=OuterRef('pk'))
        )
        actors = (
            self.model.objects.prefetch_related('persons')
            .annotate(
                actors=ArrayAgg(
                    'persons__full_name',
                    filter=Q(
                        personfilmwork__role=PersonFilmwork.PersonFilmworkRoles.actor
                    ),
                )
            )
            .filter(pk=OuterRef('pk'))
        )

        directors = (
            self.model.objects.prefetch_related('persons')
            .annotate(
                directors=ArrayAgg(
                    'persons__full_name',
                    filter=Q(
                        personfilmwork__role=PersonFilmwork.PersonFilmworkRoles.director
                    ),
                )
            )
            .filter(pk=OuterRef('pk'))
        )

        writers = (
            self.model.objects.prefetch_related('persons')
            .annotate(
                writers=ArrayAgg(
                    'persons__full_name',
                    filter=Q(
                        personfilmwork__role=PersonFilmwork.PersonFilmworkRoles.writer
                    ),
                )
            )
            .filter(pk=OuterRef('pk'))
        )

        return (
            self.model.objects.prefetch_related('genres', 'persons')
            .values()
            .annotate(
                genres=Subquery(genres.values('genres_')),
                actors=Subquery(actors.values('actors')),
                directors=Subquery(directors.values('directors')),
                writers=Subquery(writers.values('writers')),
            )
        )

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    def get_context_data(self, *, object_list=None, **kwargs):
        context = {
            'results': list(self.get_queryset()),
        }
        return context


class MoviesDetailApi(BaseDetailView):
    def get_context_data(self, *, object_list=None, **kwargs):
        context = {
            'results': list(self.get_queryset()),
        }
        return context
