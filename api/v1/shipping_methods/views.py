from django.http import Http404
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.v1.shipping_methods.serializers import ShippingMethodSerializer, SuggestedShippingMethodSerializer
from search.models import Store


class ShippingMethodViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    queryset = Store.objects.filter(is_active=True)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ShippingMethodSerializer(instance.shipping_methods.order_by('price'), many=True)
        serializer.context["request"] = request
        return Response(serializer.data)


class SuggestShippingMethodViewSet(mixins.CreateModelMixin, GenericViewSet):
    serializer_class = SuggestedShippingMethodSerializer

    def perform_create(self, serializer):
        if store := Store.objects.filter(
            is_active=True, id=self.kwargs.get("store_pk")
        ).first():
            serializer.save(store=store)
        else:
            raise Http404