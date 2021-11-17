from rest_framework import serializers

from search.models import ShippingMethod


class ShippingMethodSerializer(serializers.ModelSerializer):
    currency = serializers.CharField(source="store.currency")

    class Meta:
        model = ShippingMethod
        fields = [
            "name",
            "price",
            "min_shipping_time",
            "max_shipping_time",
            "min_price_free_shipping",
            "is_free",
            "currency",
        ]