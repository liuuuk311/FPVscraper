from rest_framework import serializers

from search.models import Store


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = [
            "name",
            "website",
            "region"
        ]