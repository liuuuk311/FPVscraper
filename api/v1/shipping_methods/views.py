from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.v1.shipping_methods.serializers import ShippingMethodSerializer
from search.models import Store


class ShippingMethodViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    queryset = Store.objects.filter(is_active=True)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ShippingMethodSerializer(instance.shipping_methods.order_by('price'), many=True)
        return Response(serializer.data)
