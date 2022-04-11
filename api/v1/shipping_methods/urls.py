from rest_framework import routers
from rest_framework_nested import routers as nested_routers
from .views import (
    ShippingMethodViewSet, SuggestShippingMethodViewSet
)

router = routers.SimpleRouter()
router.register(r"shipping_methods", ShippingMethodViewSet, basename="api_v1_shipping_methods")

shipping_router = nested_routers.NestedSimpleRouter(router, r"shipping_methods", lookup="store")
shipping_router.register(r"suggest", SuggestShippingMethodViewSet, basename="api_v1_suggest_shipping_method")

urlpatterns = router.urls + shipping_router.urls
