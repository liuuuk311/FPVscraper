from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('_secret-fpv-scraper-admin/', admin.site.urls),
    path('api/', include("api.urls")),
]
