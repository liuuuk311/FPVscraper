from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from api.v1.stores.serializers import StoreSerializer
from search.models import Store


class StoreViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = Store.objects.filter(is_active=True, is_scrapable=True)
    serializer_class = StoreSerializer