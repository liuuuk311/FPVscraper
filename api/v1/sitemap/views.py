from django.db.models import Subquery, Count, OuterRef, Prefetch
from django.utils import timezone
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from search.models import Product, Brand, ImportQuery


class SiteMapViewSet(mixins.ListModelMixin, GenericViewSet):
    MAX_PRODUCTS = 15

    def get_queryset(self):
        pass

    def list(self, request, *args, **kwargs):
        subquery = Subquery(
            Product.objects.annotate(
                click_count=Count("clicks")
            ).filter(
                brand_id=OuterRef('brand_id')
            ).order_by("-click_count").values_list('id', flat=True)[:self.MAX_PRODUCTS]
        )

        qs = Brand.objects.filter(
            is_active=True
        ).prefetch_related(
            Prefetch('products', queryset=Product.objects.filter(id__in=subquery))
        )
        timestamp = timezone.now()
        data = [
            {"query" : brand.name, "updated_at": timestamp } for brand in qs
        ]
        data.extend([{"query" : query.text, "updated_at": timestamp } for query in ImportQuery.objects.filter(is_active=True, brand__isnull=True)])
        return Response(data)