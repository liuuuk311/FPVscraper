from django.db.models import Count
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.v1.stores.serializers import StoreCountrySerializer, StoreSuggestionSerializer
from search.models import Country, Store, RequestedStore, Product


class StoreViewSet(mixins.ListModelMixin, GenericViewSet):
    """ Return the stores grouped by country """

    queryset = (
        Country.objects.filter(
            is_active=True,
        ).annotate(
            store_count=Count("stores")
        ).filter(store_count__gt=0).order_by("-store_count")
    )
    serializer_class = StoreCountrySerializer


class StoreStatsViewSet(mixins.ListModelMixin, GenericViewSet):

    def list(self, request, *args, **kwargs):
        stores_qs = Store.objects.filter(is_active=True, is_scrapable=True)

        active_stores_count = stores_qs.count()
        countries = stores_qs.distinct("country").count()
        active_products = Product.objects.filter(is_active=True, store__is_active=True, store__is_scrapable=True).count()
        return Response({
            "total_stores": active_stores_count,
            "total_countries": countries,
            "total_products": active_products
        })


class StoreSuggestionViewSet(mixins.CreateModelMixin, GenericViewSet):
    serializer_class = StoreSuggestionSerializer

    def perform_create(self, serializer):
        suggested_url = serializer.data.get("website")
        already_exists = RequestedStore.objects.filter(website=suggested_url).exists()
        RequestedStore.objects.create(website=suggested_url, is_already_present=already_exists)
