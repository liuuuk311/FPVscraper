from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from api.v1.geo.serializers import CountrySerializer, ContinentSerializer
from search.models import Country, Continent


class CountryViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = CountrySerializer

    def get_queryset(self):
        qs = Country.objects.all()
        continent = self.request.query_params.get("continent", None)
        if continent:
            qs = qs.filter(continent__id=continent)

        return qs.filter(stores__is_active=True, stores__is_scrapable=True).order_by("name").distinct()


class ContinentViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = Continent.objects.all()
    serializer_class = ContinentSerializer
