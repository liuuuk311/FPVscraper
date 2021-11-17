from rest_framework import routers
from .views import (
    ProductViewSet
)

router = routers.SimpleRouter()
router.register(r"products", ProductViewSet, basename="api_v1_products")
urlpatterns = router.urls
