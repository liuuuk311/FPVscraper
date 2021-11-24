from rest_framework import serializers

from search.models import ShippingMethod


class ShippingMethodSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
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

    def get_name(self, obj):
        lang = self.context["request"].headers.get("Accept-Language", "en")
        return getattr(obj, f"name_{lang}")