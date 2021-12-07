from django.conf import settings
from rest_framework import serializers

from search.models import Store, Country, RequestedStore


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = [
            "name",
            "website",
        ]


class CountrySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    stores = StoreSerializer(many=True)

    class Meta:
        model = Country
        fields = [
            "name",
            "stores",
        ]

    def get_name(self, obj):
        lang = self.context["request"].headers.get("Accept-Language", "en")
        if all(lang != lang_code for lang_code, _ in settings.LANGUAGES):
            return obj.name_en

        return getattr(obj, f"name_{lang}")


class StoreSuggestionSerializer(serializers.ModelSerializer):
    website = serializers.URLField()

    class Meta:
        model = RequestedStore
        fields = [
            "website"
        ]
