from rest_framework import routers

from api.v1.stores.views import StoreViewSet, StoreStatsViewSet

router = routers.SimpleRouter()
router.register(r"stores", StoreViewSet, basename="api_v1_stores")
router.register(r"stores/stats", StoreStatsViewSet, basename="api_v1_stores_stats")
urlpatterns = router.urls
