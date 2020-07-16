from django.contrib import admin

from .models import Product, Store, Category

admin.site.register(Product)
admin.site.register(Store)
admin.site.register(Category)
