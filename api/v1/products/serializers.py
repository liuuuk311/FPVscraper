from textwrap import shorten

from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from rest_framework import serializers

from search.documents import ProductDocument
from search.models import ClickedProduct, Product


class ProductSerializer(serializers.ModelSerializer):
    store = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    best_shipping_method = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'display_name',
            'price',
            'currency',
            'image',
            'link',
            'is_available',
            'store',
            'best_shipping_method',
        )

    @staticmethod
    def get_display_name(obj):
        return shorten(obj.name, width=23, placeholder="...")

    def get_store(self, obj):
        return {
            'id': obj.store.id,
            'name': obj.store.name,
        }

    def get_best_shipping_method(self, obj):
        shipping_method = obj.best_shipping_method
        lang = self.context["request"].headers.get("Accept-Language", "en").split("-")[0]
        return {
            "name": getattr(shipping_method, f"name_{lang}", "name_en"),
            "price": shipping_method.price,
            "is_free": shipping_method.is_free,
            "min_shipping_time": shipping_method.min_shipping_time,
            "min_price_shipping_condition": shipping_method.min_price_shipping_condition,
        }


class ProductDocumentSerializer(ProductSerializer, DocumentSerializer):
    store = serializers.SerializerMethodField()
    best_shipping_method = serializers.SerializerMethodField()

    class Meta:
        model = Product
        document = ProductDocument
        fields = (
            'id',
            'name',
            'display_name',
            'price',
            'currency',
            'image',
            'link',
            'is_available',
            'store',
            'best_shipping_method',
        )


class ClickedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClickedProduct
        fields = [
            "clicked_after_seconds",
            "search_query",
            "page",
        ]