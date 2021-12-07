from rest_framework import routers

from api.v1.stores.views import StoreViewSet, StoreStatsViewSet, StoreSuggestionViewSet

router = routers.SimpleRouter()
router.register(r"stores/suggest", StoreSuggestionViewSet, basename="api_v1_stores_suggest")
router.register(r"stores/stats", StoreStatsViewSet, basename="api_v1_stores_stats")
router.register(r"stores", StoreViewSet, basename="api_v1_stores")
urlpatterns = router.urls
