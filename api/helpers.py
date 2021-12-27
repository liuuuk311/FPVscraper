from django.conf import settings
from rest_framework.request import Request


def format_accept_language(lang: str) -> str:
    return lang.split("-")[0]


def get_language(request: Request) -> str:
    lang = format_accept_language(request.headers.get("Accept-Language", "en"))
    if all(lang != lang_code for lang_code, _ in settings.LANGUAGES):
        return "en"

    return lang