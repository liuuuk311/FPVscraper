from rest_framework import routers

from api.v1.geo.views import CountryViewSet, ContinentViewSet

router = routers.SimpleRouter()
router.register(r"countries", CountryViewSet, basename="api_v1_geo_countries")
router.register(r"continents", ContinentViewSet, basename="api_v1_geo_continents")
urlpatterns = router.urls
