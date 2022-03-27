from rest_framework import routers
from rest_framework_nested import routers as nested_routers
from .views import (
    ProductViewSet, ClickedProductViewSet, BestProductViewSet, ProductAutocompleteViewSet, BestBrandsViewSet
)

router = routers.SimpleRouter()
router.register(r"products/best", BestProductViewSet, basename="api_v1_best_products")
router.register(r"products/autocomplete", ProductAutocompleteViewSet, basename="api_v1_autocomplete_products")
router.register(r"products", ProductViewSet, basename="api_v1_products")
router.register(r"brands/best", BestBrandsViewSet, basename="api_v1_brands")

product_router = nested_routers.NestedSimpleRouter(router, r"products", lookup="product")
product_router.register(r"click", ClickedProductViewSet, basename="api_v1_product_clicked")

urlpatterns = router.urls + product_router.urls
