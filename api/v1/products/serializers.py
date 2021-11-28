from django.http import HttpRequest
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from rest_framework import serializers

from search.documents import ProductDocument

class ProductDocumentSerializer(DocumentSerializer):
    store = serializers.SerializerMethodField()

    class Meta:
        document = ProductDocument
        fields = (
            'id',
            'name',
            'price',
            'currency',
            'image',
            'link',
            'is_available',
            'store'
        )

    def get_store(self, obj):
        return {
            'id': obj.store.id,
            'name': obj.store.name,
            'best_shipping_method': self._get_best_shipping_method(obj)
        }

    def _get_best_shipping_method(self, obj):
        lang = self.context["request"].headers.get("Accept-Language", "en").split("-")[0]
        shipping_method = obj.store.best_shipping_method
        return {
                "name": getattr(shipping_method, f"name_{lang}", "name_en"),
                "price": shipping_method.price,
                "is_free": shipping_method.is_free,
                "min_shipping_time": shipping_method.min_shipping_time,
                "min_price_free_shipping": shipping_method.min_price_free_shipping,
            }
