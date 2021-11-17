from rest_framework import routers
from .views import (
    ShippingMethodViewSet
)

router = routers.SimpleRouter()
router.register(r"shipping_methods", ShippingMethodViewSet, basename="api_v1_shipping_methods")
urlpatterns = router.urls
