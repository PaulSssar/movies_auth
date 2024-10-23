from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

from movies.api.v1.paginator import CustomPagination
from movies.api.v1.serializers import FilmWorkSerializer
from movies.models import FilmWork


class FilmWorkViewSet(GenericViewSet,
                      ListModelMixin,
                      RetrieveModelMixin):
    serializer_class = FilmWorkSerializer
    queryset = FilmWork.objects.all()
    pagination_class = CustomPagination
