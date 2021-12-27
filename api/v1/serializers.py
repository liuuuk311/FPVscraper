from django.conf import settings
from rest_framework import serializers

from api.helpers import get_language


class TranslateNameSerializerMixin:
    context: dict

    def get_name(self, obj):
        lang = get_language(self.context["request"])

        return getattr(obj, f"name_{lang}")