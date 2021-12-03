from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.v1.stores.serializers import CountrySerializer
from search.models import Country, Store


class StoreViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = (
        Country.objects.filter(is_active=True, stores__is_active=True, stores__is_scrapable=True).distinct("name")
    )
    serializer_class = CountrySerializer


class StoreStatsViewSet(mixins.ListModelMixin, GenericViewSet):

    def list(self, request, *args, **kwargs):
        active_stores_count = Store.objects.filter(is_active=True, is_scrapable=True).count()
        return Response({
            "total_stores": active_stores_count
        })