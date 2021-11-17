from django.conf.urls import include, url

urlpatterns = [
    url(r"^", include("api.v1.products.urls")),
    url(r"^", include("api.v1.shipping_methods.urls")),
    url(r"^", include("api.v1.stores.urls")),
]