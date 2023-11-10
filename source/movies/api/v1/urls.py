from django.urls import path
from movies.api.v1.views import MoviesListApi


urlpatterns = [path('movies/', MoviesListApi.as_view())]
