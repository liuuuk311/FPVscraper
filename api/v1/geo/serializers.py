from rest_framework import serializers

from api.v1.serializers import TranslateNameSerializerMixin
from search.models import Country, Continent


class CountrySerializer(serializers.ModelSerializer, TranslateNameSerializerMixin):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = [
            "id",
            "name",
        ]


class ContinentSerializer(serializers.ModelSerializer, TranslateNameSerializerMixin):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Continent
        fields = [
            "id",
            "name",
        ]
