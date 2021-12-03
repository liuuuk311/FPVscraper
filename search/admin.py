import csv
from abc import abstractmethod
from datetime import datetime

from django.conf.urls import url
from django.contrib import admin, messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.html import format_html
from core.translation import *
from modeltranslation.admin import TranslationAdmin

from .forms import CsvImportForm
from .tasks import (
    check_scraping_compatibility,
    import_products_from_categories,
    re_import_product, import_all_products_for_all_stores,
)
from .models import Store, Category, Product, ShippingMethod, Continent, Country


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
        meta = f"Export_{datetime.today().strftime('%Y-%m-%d')}_{self.model._meta}"
        field_names = [field.name for field in self.model._meta.fields]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename={}.csv".format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"


class ImportCsv(admin.ModelAdmin):

    @abstractmethod
    def create_obj_from_dict(self, data):
        pass

    def import_csv(self, request):
        if request.method != "POST":
            form = CsvImportForm()
            payload = {"form": form}
            return render(request, "admin/import_csv_form.html", payload)

        csv_file = request.FILES["csv_file"]
        decoded_file = csv_file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)
        for row in reader:
            self.create_obj_from_dict(row)

        self.message_user(request, "Your csv file has been imported!")
        return redirect("..")


class StoreAdmin(ImportCsv, ExportCsvMixin):
    change_list_template = "admin/store_changelist.html"
    search_fields = ["name"]
    list_display = (
        "name",
        "is_scrapable",
        "imported_products",
        "products_in_stock",
        "products_out_of_stock",
        "products_with_variations",
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
                    "country",
                    "locale",
                    "scrape_with_js",
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
                    "product_description_class",
                    "product_description_tag",
                ]
            },
        ),
    ]
    actions = ["check_compatibility", "import_product", "export_as_csv"]

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

    def create_obj_from_dict(self, data):
        data.pop("id", None)
        data.pop("created_at", None)
        Store.objects.create(**data)

    def get_urls(self):
        urls = super().get_urls()
        return [
            url(
                r"import/$",
                self.admin_site.admin_view(self.import_csv),
                name="store_import_csv",
            )
        ] + urls


class ProductAdmin(admin.ModelAdmin):
    change_form_template = "admin/add_product.html"
    change_list_template = "admin/product_changelist.html"
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
                    "description",
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
            ),
            url(
               r"import_from_all_stores/$",
               self.admin_site.admin_view(self.import_from_all_stores),
               name="product_import_all",
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

    @staticmethod
    def import_from_all_stores(request):
        import_all_products_for_all_stores.delay()
        messages.success(
            request,
            "Importing ALL products for every store. It's gonna take a while",
        )
        return redirect("..")


class ShippingMethodAdmin(TranslationAdmin, ImportCsv, ExportCsvMixin):
    change_list_template = "admin/shipping_methods_changelist.html"
    actions = ["export_as_csv"]

    def create_obj_from_dict(self, data):
        store_name = data.pop("store", None).split(' ')[0]
        store = Store.objects.filter(name=store_name).first()
        if not store:
            return

        ShippingMethod.objects.create(
            store=store,
            name_it=data.get("name_it"),
            name_en=data.get("name_en"),
            min_shipping_time=data.get("min_shipping_time", None) or None,
            max_shipping_time=data.get("max_shipping_time", None) or None,
            price=data.get("price", None) or None,
            min_price_free_shipping=data.get("min_price_free_shipping", None) or None,
            is_active=data.get("is_active", False)
        )

    def get_urls(self):
        urls = super().get_urls()
        return [
            url(
                r"import/$",
                self.admin_site.admin_view(self.import_csv),
                name="shipping_methods_import_csv",
            )
        ] + urls


class ContinentAdmin(TranslationAdmin, ImportCsv, ExportCsvMixin):
    change_list_template = "admin/continent_changelist.html"
    actions = ["export_as_csv"]

    def create_obj_from_dict(self, data):
        Continent.objects.create(
            name_it=data.get("name_it"),
            name_en=data.get("name_en"),
            is_active=data.get("is_active", False)
        )

    def get_urls(self):
        urls = super().get_urls()
        return [
            url(
                r"import/$",
                self.admin_site.admin_view(self.import_csv),
                name="continent_import_csv",
            )
        ] + urls


class CountryAdmin(TranslationAdmin, ImportCsv, ExportCsvMixin):
    change_list_template = "admin/country_changelist.html"
    actions = ["export_as_csv"]

    def create_obj_from_dict(self, data):
        continent_name = data.pop("continent", None).split(' ')[0]
        continent = Continent.objects.filter(name=continent_name).first()
        if not continent:
            return

        Country.objects.create(
            continent=continent,
            name_it=data.get("name_it"),
            name_en=data.get("name_en"),
            is_active=data.get("is_active", False)
        )

    def get_urls(self):
        urls = super().get_urls()
        return [
            url(
                r"import/$",
                self.admin_site.admin_view(self.import_csv),
                name="country_import_csv",
            )
        ] + urls


admin.site.register(Store, StoreAdmin)
admin.site.register(ShippingMethod, ShippingMethodAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(Continent, ContinentAdmin)
admin.site.register(Country, CountryAdmin)
