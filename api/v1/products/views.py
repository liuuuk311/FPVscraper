from datetime import datetime, timedelta

from django.db.models import Count
from django_elasticsearch_dsl_drf.constants import (
    SUGGESTER_COMPLETION,
)
from django_elasticsearch_dsl_drf.filter_backends import (
    CompoundSearchFilterBackend, DefaultOrderingFilterBackend, OrderingFilterBackend, FilteringFilterBackend,
    SearchFilterBackend,
)
from django_elasticsearch_dsl_drf.viewsets import BaseDocumentViewSet
from django_elasticsearch_dsl_drf.pagination import PageNumberPagination
from rest_framework import mixins, viewsets

from search.documents import ProductDocument
from api.v1.products.serializers import ProductDocumentSerializer, ClickedProductSerializer, ProductSerializer
from search.models import ClickedProduct, Product


class ProductViewSet(BaseDocumentViewSet):
    document = ProductDocument
    serializer_class = ProductDocumentSerializer
    pagination_class = PageNumberPagination
    lookup_field = 'id'

    filter_backends = [
        FilteringFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        CompoundSearchFilterBackend,
    ]

    search_fields = {
        'name': {'boost': 4},
        'description': None,
    }

    filter_fields = {
        'name': 'name.raw',
        'description': 'description.raw',
        'is_available': 'is_available.raw',
    }

    suggester_fields = {
        'name_suggest': {
            'field': 'name.suggest',
            'suggesters': [
                SUGGESTER_COMPLETION,
            ],
        },
    }

    ordering_fields = {
        'price': 'price',
        'name': 'name.raw',
        'score': '_score',
        'clicks': 'click_score',
    }

    # ordering = ('_score', '-price')


class ClickedProductViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = ClickedProductSerializer

    def perform_create(self, serializer):
        product_qs = Product.objects.filter(id=self.kwargs.get("product_id"))
        if not product_qs.exists():
            return

        ClickedProduct.objects.create(
            product=product_qs.first(),
            **serializer.data
        )


class BestProductViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(
            clicks__isnull=False
        ).annotate(
            click_count=Count("clicks")
        ).order_by("-click_count").distinct()[:10]
