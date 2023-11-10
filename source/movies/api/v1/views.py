from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from movies.models import Filmwork


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    def get_queryset(self):
        return  # Сформированный QuerySet

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset, self.paginate_by
        )
        # some code
        return {
            'count': paginator.count,
        }


class MoviesDetailApi(BaseDetailView):
    def get_context_data(self, *, object_list=None, **kwargs):
        context = {
            'results': list(self.get_queryset()),
        }
        return context
