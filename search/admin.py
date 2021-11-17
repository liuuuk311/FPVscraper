from celery import group
from django.conf.urls import url
from django.contrib import admin, messages
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.html import format_html

from .tasks import check_scraping_compatibility, import_products_from_categories, re_import_product
from .models import Store, Category, Product, ShippingMethod


class StoreAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = (
        "name",
        "is_scrapable",
        "last_check",
    )
    readonly_fields = ("is_scrapable", "not_scrapable_reason")
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "name",
                    "website",
                    "region",
                    "locale",
                    "is_scrapable",
                    "not_scrapable_reason",
                ]
            },
        ),
        (
            "Search",
            {
                "fields": [
                    "search_url",
                    "search_tag",
                    "search_class",
                    "search_link",
                    "search_next_page",
                ]
            },
        ),
        (
            "Product",
            {
                "fields": [
                    "product_name_class",
                    "product_name_tag",
                    "product_price_class",
                    "product_price_tag",
                    "product_image_class",
                    "product_image_tag",
                    "product_is_available_class",
                    "product_is_available_tag",
                    "product_is_available_match",
                    "product_variations_class",
                    "product_variations_tag",
                ]
            },
        ),
    ]
    actions = ["check_compatibility", "import_product"]

    def check_compatibility(self, request, queryset):
        for store in queryset:
            check_scraping_compatibility.delay(store.pk)

        self.message_user(
            request,
            "A task has been launched to check the compatibilities.",
            messages.SUCCESS,
        )

    def import_product(self, request, queryset):
        for store in queryset:
            import_products_from_categories.delay(store.pk)

        self.message_user(
            request,
            "A task has been launched to import products from categories.",
            messages.SUCCESS,
        )


class ProductAdmin(admin.ModelAdmin):
    change_form_template = "admin/add_product.html"
    search_fields = ["name"]
    list_display = (
        "name",
        "is_available",
        "price",
        "import_date",
        "store",
    )
    readonly_fields = ("import_date", "image_tag", "id", "original_link")
    list_filter = ("is_available", "store")
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "image_tag",
                    "name",
                    "is_available",
                    "price",
                    "currency",
                    "store",
                ]
            },
        ),
        (
            "Advanced",
            {"fields": ["original_link", "import_date", "id"]},
        ),
    ]

    @staticmethod
    def original_link(obj):
        return format_html(f'<a href="{obj.link}" target="_blank">Open</a>')

    def image_tag(self, obj):
        return format_html(
            f'<img src="{obj.image}" height="200" alt="Image of {obj.name}"/>'
        )

    image_tag.short_description = ""

    def get_urls(self):
        urls = super(ProductAdmin, self).get_urls()
        return [
            url(
                r"^(?P<product_id>.+)/import/$",
                self.admin_site.admin_view(self.product_import),
                name="product_import",
            )
        ] + urls

    def product_import(self, request, product_id):
        product = self.get_object(request, product_id)
        re_import_product.delay(product_id)
        messages.success(
            request,
            f"Starting to re-import {product.name} from {product.store.name}. Refresh the page to see the new data.",
        )
        return redirect("admin:search_product_change", product_id)


admin.site.register(Store, StoreAdmin)
admin.site.register(ShippingMethod)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
