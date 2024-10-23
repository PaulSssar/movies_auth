from django.urls import include, path
from rest_framework.routers import DefaultRouter

from movies.api.v1.views import FilmWorkViewSet

router_v1 = DefaultRouter(trailing_slash=False)

router_v1.register('movies', FilmWorkViewSet, basename='movie', )

urlpatterns = [
    path('', include(router_v1.urls)),
]
