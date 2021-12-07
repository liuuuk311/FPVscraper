from rest_framework import routers
from rest_framework_nested import routers as nested_routers
from .views import (
    ProductViewSet, ClickedProductViewSet, BestProductViewSet
)

router = routers.SimpleRouter()
router.register(r"products/best", BestProductViewSet, basename="api_v1_best_products")
router.register(r"products", ProductViewSet, basename="api_v1_products")

product_router = nested_routers.NestedSimpleRouter(router, r"products", lookup="product")
product_router.register(r"click", ClickedProductViewSet, basename="api_v1_product_clicked")

urlpatterns = router.urls + product_router.urls
