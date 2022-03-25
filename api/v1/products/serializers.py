from textwrap import shorten

from rest_framework import serializers

from api.helpers import format_accept_language
from search.models import ClickedProduct, Product, Brand


class ProductSerializer(serializers.ModelSerializer):
    store = serializers.SerializerMethodField()
    best_shipping_method = serializers.SerializerMethodField()
    link = serializers.CharField(source="affiliate_link")

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'price',
            'currency',
            'image',
            'link',
            'is_available',
            'store',
            'best_shipping_method',
        )

    @staticmethod
    def get_store(obj):
        return {
            'id': obj.store.id,
            'name': obj.store.name,
        }

    def get_best_shipping_method(self, obj):
        shipping_method = obj.best_shipping_method
        if not shipping_method:
            return

        lang = format_accept_language(self.context["request"].headers.get("Accept-Language", "en"))
        return {
            "name": getattr(shipping_method, f"name_{lang}", "name_en"),
            "price": shipping_method.price,
            "is_free": shipping_method.is_free,
            "min_shipping_time": shipping_method.min_shipping_time,
            "min_price_shipping_condition": shipping_method.min_price_shipping_condition,
            "is_weight_dependent": shipping_method.is_weight_dependent,
        }


class ProductAutocompleteSerializer(ProductSerializer):
    class Meta:
        model = Product
        fields = (
            'name',
        )

class ClickedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClickedProduct
        fields = [
            "clicked_after_seconds",
            "search_query",
            "page",
        ]

class BrandProductsSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    products = ProductSerializer(many=True)

    class Meta:
        model = Brand
        fields = [
            "name",
            "description",
            "logo",
            "products",
        ]

    def get_description(self, obj):
        lang = format_accept_language(self.context["request"].headers.get("Accept-Language", "en"))
        return getattr(obj, f"description_{lang}", "description_en")