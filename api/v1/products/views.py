from django_elasticsearch_dsl_drf.constants import (
    SUGGESTER_COMPLETION,
)
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    CompoundSearchFilterBackend,
)
from django_elasticsearch_dsl_drf.viewsets import BaseDocumentViewSet
from django_elasticsearch_dsl_drf.pagination import PageNumberPagination

from search.documents import ProductDocument
from api.v1.products.serializers import ProductDocumentSerializer


class ProductViewSet(BaseDocumentViewSet):
    document = ProductDocument
    serializer_class = ProductDocumentSerializer
    pagination_class = PageNumberPagination
    lookup_field = 'id'

    filter_backends = [
        FilteringFilterBackend,
        CompoundSearchFilterBackend,
    ]

    search_fields = (
        'name',
    )

    filter_fields = {
        'name': 'name.raw',
    }

    suggester_fields = {
        'name_suggest': {
            'field': 'name.suggest',
            'suggesters': [
                SUGGESTER_COMPLETION,
            ],
        },
    }