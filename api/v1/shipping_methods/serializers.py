from rest_framework import serializers

from api.v1.geo.serializers import CountrySerializer
from api.v1.serializers import TranslateNameSerializerMixin
from search.models import ShippingMethod


class ShippingMethodSerializer(serializers.ModelSerializer, TranslateNameSerializerMixin):
    name = serializers.SerializerMethodField()
    currency = serializers.CharField(source="store.currency")
    countries = CountrySerializer(source="shipping_zone.ship_to", many=True, required=False)

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
            "is_weight_dependent",
            "countries",
        ]