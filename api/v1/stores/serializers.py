from rest_framework import serializers

from api.v1.geo.serializers import CountrySerializer
from search.models import Store, Country, RequestedStore


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = [
            "name",
            "website",
        ]


class StoreCountrySerializer(CountrySerializer):
    name = serializers.SerializerMethodField()
    stores = StoreSerializer(many=True)

    class Meta:
        model = Country
        fields = [
            "name",
            "stores",
        ]


class StoreSuggestionSerializer(serializers.ModelSerializer):
    website = serializers.URLField()

    class Meta:
        model = RequestedStore
        fields = [
            "website"
        ]
