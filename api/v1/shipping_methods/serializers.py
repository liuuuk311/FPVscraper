from rest_framework import serializers

from api.v1.serializers import TranslateNameSerializerMixin
from search.models import ShippingMethod


class ShippingMethodSerializer(serializers.ModelSerializer, TranslateNameSerializerMixin):
    name = serializers.SerializerMethodField()
    currency = serializers.CharField(source="store.currency")

    class Meta:
        model = ShippingMethod
        fields = [
            "name",
            "price",
            "min_shipping_time",
            "max_shipping_time",
            "min_price_shipping_condition",
            "is_free",
            "currency",
        ]
