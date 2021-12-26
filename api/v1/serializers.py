from django.conf import settings
from rest_framework import serializers


class TranslateNameSerializerMixin(serializers.BaseSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        lang = self.context["request"].headers.get("Accept-Language", "en")
        if all(lang != lang_code for lang_code, _ in settings.LANGUAGES):
            return obj.name_en

        return getattr(obj, f"name_{lang}")