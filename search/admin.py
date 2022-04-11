import csv
import itertools
from abc import abstractmethod
from datetime import datetime, timedelta
from typing import List

from django.conf.urls import url
from django.contrib import admin, messages
from django.db.models import Count
from django.http import StreamingHttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.html import format_html
from core.translation import *
from modeltranslation.admin import TranslationAdmin

from .forms import CsvImportForm
from .tasks import (
    check_scraping_compatibility,
    task_search_and_import_store_products,
    task_re_import_product,
    task_search_and_import_products_from_active_stores,
    task_re_import_product_from_active_stores,
    task_re_import_product_from_store,
)
from .models import (
    Store,
    ImportQuery,
    Product,
    ShippingMethod,
    Continent,
    Country,
    ClickedProduct,
    RequestedStore,
    ShippingZone, SuggestedShippingMethod
)


class PseudoBuffer:
    """ An object that implements just the write method of the file-like interface """

    @staticmethod
    def write(value):
        """ Write the value by returning it, instead of storing in a buffer """
        return value


class ExportCsv(admin.ModelAdmin):
    actions = ["export_as_csv"]

    def get_field_names(self) -> List:
        return [field.name for field in self.model._meta.fields]

    def get_row(self, obj) -> List:
        return [getattr(obj, field) for field in self.get_field_names()]

    def get_header(self) -> str:
        return ",".join(self.get_field_names()) + "\n"

    def get_name(self) -> str:
        return f"Export_{datetime.today().strftime('%Y-%m-%d')}_{self.model._meta}"

    def export_as_csv(self, request, queryset):
        buffer = PseudoBuffer()
        writer = csv.writer(buffer)

        rows = itertools.chain(self.get_header(), (writer.writerow(self.get_row(obj)) for obj in queryset))
        return StreamingHttpResponse(
            rows,
            content_type="text/csv",
            headers={'Content-Disposition': f'attachment;filename="{self.get_name()}.csv"'}
        )

    export_as_csv.short_description = "Export Selected"

    def export_all(self, request):
        return self.export_as_csv(request, self.model.objects.all())

    def get_urls(self):
        urls = super().get_urls()
        return [
            url(
                r"export/$",
                self.admin_site.admin_view(self.export_all),
                name=self.export_url_name,
            )
        ] + urls

    @property
    def export_url_name(self):
        return f"{self.model._meta.verbose_name_plural.replace(' ', '_')}_export_all"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update({'export_url': self.export_url_name})
        return super().changelist_view(request, extra_context=extra_context)


class ManyToManyExport:
    many_to_many_field: str

    def many_to_many_fields_names(self):
        return [
            f"{self.many_to_many_field}_{i}"
            for i in range(
                self.model.objects.all().annotate(
                    count=Count(self.many_to_many_field)
                ).values_list("count", flat=True).order_by("-count")[0])
        ]

    def get_field_names(self):
        return super().get_field_names() + self.many_to_many_fields_names()

    def get_many_to_many_list(self, obj):
        m2m = list(getattr(obj, self.many_to_many_field).all())
        return m2m + ([''] * (len(self.many_to_many_fields_names()) - len(m2m)))

    def get_row(self, obj):
        many_to_many_fields_num = len(self.many_to_many_fields_names())
        return [
                   getattr(obj, field) for field in self.get_field_names()[:-many_to_many_fields_num]
               ] + self.get_many_to_many_list(obj)


class ImportCsv(admin.ModelAdmin):

    @abstractmethod
    def create_obj_from_dict(self, data):
        raise NotImplemented

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

    def get_urls(self):
        urls = super().get_urls()
        return [
            url(
                r"import/$",
                self.admin_site.admin_view(self.import_csv),
                name=self.import_url_name,
            )
        ] + urls

    @property
    def import_url_name(self):
        return f"{self.model._meta.verbose_name_plural.replace(' ', '_')}_import_csv"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update({'import_url': self.import_url_name})
        return super().changelist_view(request, extra_context=extra_context)


class ImportExportMixin(ImportCsv, ExportCsv):
    change_list_template = "admin/import_export_changelist.html"

    @abstractmethod
    def create_obj_from_dict(self, data):
        raise NotImplemented


class StoreAdmin(ImportExportMixin):
    change_form_template = "admin/change_store.html"
    search_fields = ["name"]
    list_display = (
        "name",
        "is_scrapable",
        "has_shipping_methods",
        "imported_products",
        "products_in_stock",
        "products_out_of_stock",
        "products_with_variations",
        "products_not_active",
        "last_check",
    )
    readonly_fields = ("is_scrapable", "not_scrapable_reason", "logo_tag", "has_shipping_methods",)
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "logo_tag",
                    "name",
                    "website",
                    "is_active",
                    "country",
                    "currency",
                    "logo",
                    "affiliate_query_param",
                    "affiliate_id",
                ]
            },
        ),
        (
            "Scraping Settings",
            {
                "fields": [
                    "locale",
                    "scrape_with_js",
                    "is_scrapable",
                    "not_scrapable_reason",
                ]
            }
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
                    "search_page_param",
                ]
            },
        ),
        (
            "Product",
            {
                "fields": [
                    ("product_name_class", "product_name_css_is_class", "product_name_tag",),
                    ("product_price_class", "product_price_css_is_class", "product_price_tag",),
                    ("product_image_class", "product_image_css_is_class", "product_image_tag",),
                    ("product_is_available_class", "product_is_available_css_is_class", "product_is_available_tag", "product_is_available_match",),
                    ("product_variations_class", "product_variations_css_is_class", "product_variations_tag",),
                    ("product_description_class", "product_description_css_is_class", "product_description_tag",),
                ]
            },
        ),
    ]
    actions = ["check_compatibility", "search_and_import_product", "export_as_csv"]

    def check_compatibility(self, request, queryset):
        for store in queryset:
            check_scraping_compatibility.delay(store.pk)

        self.message_user(
            request,
            "A task has been launched to check the compatibilities.",
            messages.SUCCESS,
        )

    def search_and_import_product(self, request, queryset):
        for store in queryset:
            task_search_and_import_store_products.delay(store.pk)

        self.message_user(
            request,
            "A task has been launched to import products from import queries.",
            messages.SUCCESS,
        )

    def create_obj_from_dict(self, data):
        data.pop("id", None)
        data.pop("created_at", None)
        data["country"] = Country.objects.filter(name=data.get("country")).first()
        Store.objects.update_or_create(website=data.get("website"), defaults=data)

    def get_urls(self):
        urls = super(StoreAdmin, self).get_urls()
        return [
            url(
               r"^(?P<store_id>.+)/import_all_with_queries/$",
               self.admin_site.admin_view(self.import_with_queries),
               name="store_product_import_all_with_queries",
            ),
            url(
               r"^(?P<store_id>.+)/import_all/$",
               self.admin_site.admin_view(self.import_all),
               name="store_product_import_all",
           )
        ] + urls

    @staticmethod
    def import_with_queries(request, store_id):
        task_search_and_import_store_products.delay(store_id)
        messages.success(
            request,
            "Importing ALL products for every store. It's gonna take a while",
        )
        return redirect("..")

    @staticmethod
    def import_all(request, store_id):
        task_re_import_product_from_store.delay(store_id)
        messages.success(
            request,
            "Re Importing ALL products. It's gonna take a while",
        )
        return redirect("..")

    def has_shipping_methods(self, obj) -> bool:
        return obj.shipping_methods.exists()

    has_shipping_methods.boolean = True


class ProductAdmin(ImportExportMixin):
    change_form_template = "admin/change_product.html"
    change_list_template = "admin/product_changelist.html"
    search_fields = ["name"]
    list_display = (
        "name",
        "is_available",
        "price",
        "import_date",
        "store",
        "brand",
    )
    readonly_fields = (
        "import_date",
        "image_tag",
        "id",
        "original_link",
        "import_query"
    )
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
                    "brand"
                ]
            },
        ),
        (
            "Advanced",
            {"fields": ["original_link", "import_date", "import_query", "is_active", "id"]},
        ),
    ]

    @staticmethod
    def original_link(obj):
        return format_html(f'<a href="{obj.link}" target="_blank">Open</a>')

    def image_tag(self, obj):
        return format_html(
            f'<img src="{obj.image}" width="300" height="300" alt="Image of {obj.name}"/>'
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
               r"import_all_with_queries/$",
               self.admin_site.admin_view(self.import_from_all_stores),
               name="product_import_all_with_queries",
            ),
            url(
               r"import_all/$",
               self.admin_site.admin_view(self.import_all),
               name="product_import_all",
           )
        ] + urls

    def product_import(self, request, product_id):
        product = self.get_object(request, product_id)
        task_re_import_product.delay(product_id)
        messages.success(
            request,
            f"Starting to re-import {product.name} from {product.store.name}. Refresh the page to see the new data.",
        )
        return redirect("admin:search_product_change", product_id)

    @staticmethod
    def import_from_all_stores(request):
        task_search_and_import_products_from_active_stores.delay()
        messages.success(
            request,
            "Importing ALL products for every store. It's gonna take a while",
        )
        return redirect("..")

    @staticmethod
    def import_all(request):
        task_re_import_product_from_active_stores.delay(Store.objects.filter(is_active=True))
        messages.success(
            request,
            "Re Importing ALL products. It's gonna take a while",
        )
        return redirect("..")


class ShippingMethodAdmin(TranslationAdmin, ImportExportMixin):

    list_display = (
        "display_name",
        "price",
        "is_free"
    )
    readonly_fields = ("created_at", )

    def create_obj_from_dict(self, data):
        store_name = data.pop("store", "").split(' (')[0]
        store = Store.objects.filter(name=store_name).first()
        if not store:
            return

        shipping_zone = ShippingZone.objects.filter(name=data.get("shipping_zone")).first()

        try:
            price = float(data.get("price"))
        except (TypeError, ValueError):
            price = None

        try:
            min_price_shipping_condition = float(data.get("min_price_shipping_condition"))
        except (TypeError, ValueError):
            min_price_shipping_condition = None

        ShippingMethod.objects.create(
            store=store,
            shipping_zone=shipping_zone,
            name=data.get("name"),
            name_it=data.get("name_it"),
            name_en=data.get("name_en"),
            min_shipping_time=data.get("min_shipping_time", None) or None,
            max_shipping_time=data.get("max_shipping_time", None) or None,
            currency=data.get("currency"),
            price=price,
            min_price_shipping_condition=min_price_shipping_condition,
            is_active=data.get("is_active", False),
            is_vat_included=data.get("is_vat_included", True),
            is_weight_dependent=data.get("is_weight_dependent", True)
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


class ContinentAdmin(TranslationAdmin, ImportExportMixin):
    readonly_fields = ("created_at",)

    def create_obj_from_dict(self, data):
        Continent.objects.create(
            name_it=data.get("name_it"),
            name_en=data.get("name_en"),
            is_active=data.get("is_active", False)
        )


class CountryAdmin(TranslationAdmin, ImportExportMixin):
    readonly_fields = ("created_at",)

    def create_obj_from_dict(self, data):
        continent_name = data.pop("continent", "").split(' ')[0]
        continent = Continent.objects.filter(name=continent_name).first()
        if not continent:
            return

        Country.objects.get_or_create(
            continent=continent,
            name_it=data.get("name_it"),
            name_en=data.get("name_en"),
            is_active=data.get("is_active", False)
        )


class ClickedProductAdmin(admin.ModelAdmin):
    change_list_template = "admin/clicked_products_changelist.html"
    readonly_fields = (
        "product",
        "clicked_after_seconds",
        "search_query",
        "page",
        "created_at",
    )
    exclude = ("is_active", )
    list_display = (
        "product",
        "store",
        "search_query",
        "created_at",
    )

    @staticmethod
    def dashboard_data():
        data = []
        stores = Store.objects.only_active()
        for store in stores:
            qs = ClickedProduct.objects.filter(product__store=store)
            if qs.count() == 0:
                continue

            now = timezone.now()
            last_week_clicks = qs.created_after(now - timedelta(days=7)).count()
            last_month_clicks = qs.created_after(now - timedelta(days=30)).count()
            if last_month_clicks == 0:
                continue

            data.append(
                {
                    "store_name": store.name,
                    "total": qs.count(),
                    "last_7_days": last_week_clicks,
                    "last_1_month": last_month_clicks
                }
            )
        return data

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update({'dashboard_data': self.dashboard_data()})
        return super().changelist_view(request, extra_context=extra_context)

class RequestedStoreAdmin(admin.ModelAdmin):
    change_list_template = "admin/requested_store_changelist.html"
    readonly_fields = (
        "website",
        "is_already_present"
    )
    exclude = ("is_active",)
    list_display = ("website", "created_at",)

    @staticmethod
    def priority_table():
        already_added_urls = Store.objects.values_list("website")
        return RequestedStore.objects.exclude(
            website__in=already_added_urls
        ).values("website").annotate(total=Count("website")).order_by("-total")[:5]

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update({'priority_table': self.priority_table()})
        return super().changelist_view(request, extra_context=extra_context)


class ShippingZoneAdmin(ManyToManyExport, ImportExportMixin):
    readonly_fields = ("created_at",)
    many_to_many_field = "ship_to"

    def create_obj_from_dict(self, data):
        sz = ShippingZone.objects.create(
            is_active=data.get("is_active", False),
            name=data.get("name")
        )
        for field in data:
            if not field.startswith(self.many_to_many_field):
                continue

            country = Country.objects.filter(name=data.get(field))
            if not country.exists():
                continue

            getattr(sz, self.many_to_many_field).add(country.first())


class BrandAdmin(ImportExportMixin):
    readonly_fields = ("created_at",)

    def create_obj_from_dict(self, data):
        data.pop("id", None)
        data.pop("created_at", None)
        Brand.objects.create(**data)


class ImportQueryAdmin(ImportExportMixin):
    readonly_fields = ("priority_score", "created_at",)
    exclude = ("products_clicks", )

    def create_obj_from_dict(self, data):
        data.pop("id", None)
        data.pop("created_at", None)
        ImportQuery.objects.create(**data)


admin.site.register(Store, StoreAdmin)
admin.site.register(ShippingMethod, ShippingMethodAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ImportQuery, ImportQueryAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Continent, ContinentAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(ClickedProduct, ClickedProductAdmin)
admin.site.register(RequestedStore, RequestedStoreAdmin)
admin.site.register(ShippingZone, ShippingZoneAdmin)
admin.site.register(SuggestedShippingMethod)
