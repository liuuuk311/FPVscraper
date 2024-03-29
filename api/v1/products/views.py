from distutils.util import strtobool

from django.contrib.postgres.search import SearchQuery, TrigramSimilarity
from django.db.models import Count, Subquery, OuterRef, Prefetch
from rest_framework import mixins, viewsets

from api.v1.products.serializers import ClickedProductSerializer, ProductSerializer, \
    ProductAutocompleteSerializer, BrandProductsSerializer
from search.models import ClickedProduct, Product, Brand


class ProductViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        query = self.request.query_params.get("search")
        availability_filter = self.request.query_params.get("is_available")
        continent_filter = self.request.query_params.get("continent")
        country_filter = self.request.query_params.get("country")

        qs = Product.objects.filter(
            is_active=True, store__is_active=True,
        )

        if availability_filter is not None:
            qs = qs.filter(is_available=bool(strtobool(availability_filter)))

        if continent_filter is not None:
            qs = qs.filter(store__country__continent_id=int(continent_filter))

        if country_filter is not None:
            qs = qs.filter(store__country_id=int(country_filter))

        results = qs.filter(
            search_vector=SearchQuery(query)
        )
        if results.count() > 0:
            return results.annotate(
                clicks_count=Count("clicks")
            ).order_by('-clicks_count')

        return qs.annotate(
            similarity=TrigramSimilarity('name', query),
        ).filter(similarity__gt=0.15).order_by('-similarity')


class ProductAutocompleteViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductAutocompleteSerializer

    def get_queryset(self):
        query = self.request.query_params.get("q")

        qs = Product.objects.filter(
            is_active=True, store__is_active=True
        )

        return qs.annotate(
            similarity=TrigramSimilarity('name', query),
        ).annotate(
            clicks_count=Count("clicks")
        ).filter(similarity__gt=0.15).order_by('-clicks_count', '-similarity')[:12]


class ClickedProductViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = ClickedProductSerializer

    def perform_create(self, serializer):
        product_qs = Product.objects.filter(id=self.kwargs.get("product_pk"))
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
            clicks__isnull=False, is_active=True, store__is_active=True
        ).annotate(
            click_count=Count("clicks")
        ).order_by("-click_count").distinct()[:6]


class BestBrandsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = BrandProductsSerializer
    MAX_PRODUCTS = 6

    def get_queryset(self):
        subquery = Subquery(
            Product.objects.annotate(
                click_count=Count("clicks")
            ).filter(
                brand_id=OuterRef('brand_id')
            ).order_by("-click_count").values_list('id', flat=True)[:self.MAX_PRODUCTS]
        )

        return Brand.objects.filter(
            is_active=True, is_hot=True
        ).prefetch_related(
            Prefetch('products', queryset=Product.objects.filter(id__in=subquery))
        )


