from rest_framework import routers

from api.v1.stores.views import StoreViewSet

router = routers.SimpleRouter()
router.register(r"stores", StoreViewSet, basename="api_v1_stores")
urlpatterns = router.urls
