from rest_framework import routers

from api.v1.sitemap.views import SiteMapViewSet

router = routers.SimpleRouter()
router.register(r"sitemap", SiteMapViewSet, basename="api_v1_sitemap")
urlpatterns = router.urls
