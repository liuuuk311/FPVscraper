from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.safestring import mark_safe

from helpers.models import BaseModel


class StoreQuerySet(QuerySet):
    def only_active(self):
        return self.filter(is_active=True)

    def only_asian(self):
        asia = Continent.objects.filter(name_en="Asia").first()
        return self.only_active().filter(country__continent=asia)

    def only_european(self):
        europe = Continent.objects.filter(name_en="Europe").first()
        return self.only_active().filter(country__continent=europe)

    def only_american(self):
        america = Continent.objects.filter(name_en="America").first()
        return self.only_active().filter(country__continent=america)

    def only_australian(self):
        oceania = Continent.objects.filter(name_en="Oceania").first()
        return self.only_active().filter(country__continent=oceania)


class Store(BaseModel):
    """This model represent an online store"""

    CURRENCIES = (
        ("EUR", "Euro"),
        ("USD", "US Dollar"),
        ("GBP", "British Pound"),
        ("CAD", "Canadian Dollar"),
        ("AUD", "Australian Dollar"),

    )

    LOCALE_US = "en_US"
    LOCALE_EU = "it_IT"
    LOCALE = ((LOCALE_US, "American"), (LOCALE_EU, "European"))

    name = models.CharField("Name of the store", max_length=256)
    website = models.URLField("URL of the store")
    logo = models.ImageField("Logo", default=None, null=True, blank=True, upload_to ='uploads/')
    country = models.ForeignKey("Country", related_name="stores", null=True, default=None, on_delete=models.SET_NULL)
    locale = models.CharField(
        "Locale used in the store",
        max_length=5,
        choices=LOCALE,
        default=LOCALE_EU,
        help_text="If the store uses , as decimal separator choose European",
    )
    currency = models.CharField(
        "Default Currency", max_length=3, choices=CURRENCIES, default="EUR"
    )
    last_check = models.DateTimeField("Last check", null=True)

    is_scrapable = models.BooleanField("Is the store still compatible?", default=False)
    not_scrapable_reason = models.CharField(
        "The reason why this store was not scrapable",
        max_length=512,
        null=True,
        blank=True,
    )
    scrape_with_js = models.BooleanField("Use JS when scraping", default=False)

    # Scraping config
    search_url = models.URLField("The base url of the search page")
    search_tag = models.CharField(
        "The nearest html tag for each product item displayed in the result page",
        max_length=64,
    )
    search_class = models.CharField(
        "The nearest css class for the search_tag", max_length=64
    )
    search_link = models.CharField(
        "The nearest css class from where to search the product page link",
        max_length=64,
    )
    search_next_page = models.CharField(
        "The nearest css class from where to get the next page link",
        max_length=64,
        null=True,
        blank=True,
    )
    search_page_param = models.CharField(
        "The query param used in alternative to the next page link",
        max_length=64,
        null=True,
        blank=True,
    )
    product_name_class = models.CharField(
        "CSS class/id for Product's name", max_length=64
    )
    product_name_css_is_class = models.BooleanField(
        "CSS is a class",
        default=True,
    )
    product_name_tag = models.CharField(
        "HTML tag for the product's name", max_length=64
    )
    product_price_class = models.CharField(
        "CSS class/id for Product's price", max_length=64
    )
    product_price_css_is_class = models.BooleanField(
        "CSS is a class",
        default=True,
    )
    product_price_tag = models.CharField(
        "HTML tag for the product's price", max_length=64
    )
    product_image_class = models.CharField(
        "CSS class/id for Product's image",
        max_length=64,
        null=True,
        blank=True,
    )
    product_image_css_is_class = models.BooleanField(
        "CSS is a class",
        default=True,
    )
    product_image_tag = models.CharField(
        "HTML tag for the main image of the product",
        max_length=64,
        null=True,
        blank=True,
    )
    product_thumb_class = models.CharField(
        "CSS class/id for Product's thumbnail",
        max_length=64,
        null=True,
        blank=True,
    )
    product_thumb_css_is_class = models.BooleanField(
        "CSS is a class",
        default=True,
    )
    product_thumb_tag = models.CharField(
        "HTML tag for the thumbnail images of the product",
        max_length=64,
        null=True,
        blank=True,
    )
    product_is_available_class = models.CharField(
        "CSS class/id to know if the product is available",
        max_length=64,
        null=True,
        blank=True,
    )
    product_is_available_css_is_class = models.BooleanField(
        "CSS is a class",
        default=True,
    )
    product_is_available_tag = models.CharField(
        "HTML tag to know if the product is available",
        max_length=64,
        null=True,
        blank=True,
    )
    product_is_available_match = models.CharField(
        "Regex to match if the product is in stock",
        max_length=128,
        null=True,
        blank=True,
    )
    product_variations_class = models.CharField(
        "CSS class/id to know if the product has variations",
        max_length=64,
        null=True,
        blank=True,
    )
    product_variations_css_is_class = models.BooleanField(
        "CSS is a class",
        default=True,
    )
    product_variations_tag = models.CharField(
        "HTML tag to know if the product has variations",
        max_length=64,
        null=True,
        blank=True,
    )
    product_description_class = models.CharField(
        "CSS class/id for Product's description",
        max_length=64,
        null=True,
        blank=True,
    )
    product_description_css_is_class = models.BooleanField(
        "CSS is a class",
        default=True,
    )
    product_description_tag = models.CharField(
        "HTML tag to know if the product description",
        max_length=64,
        null=True,
        blank=True,
    )

    affiliate_query_param = models.CharField(
        "The affiliate query parameter",
        max_length=64,
        null=True,
        blank=True,
    )
    affiliate_id =  models.CharField(
        "The affiliate id",
        max_length=256,
        null=True,
        blank=True,
    )

    objects = StoreQuerySet.as_manager()

    def __str__(self):
        return "{} ({})".format(
            self.name,
            self.website,
        )

    def logo_tag(self):
        return mark_safe(f'<img src="{self.logo.url}" width="33%" />')

    logo_tag.short_description = 'Logo'

    def set_is_not_scrapable(self, reason: str):
        self.not_scrapable_reason = reason
        self.last_check = timezone.now()
        self.is_scrapable = False
        self.save()

    def set_is_scrapable(self):
        self.not_scrapable_reason = ""
        self.last_check = timezone.now()
        self.is_scrapable = True
        self.save()

    def best_shipping_method(self) -> "ShippingMethod":
        return self.shipping_methods.order_by("price", "name").first()

    @property
    def imported_products(self) -> int:
        return self.products.count()

    @property
    def products_in_stock(self) -> int:
        return self.products.only_active().filter(is_available=True).count()

    @property
    def products_out_of_stock(self) -> int:
        return self.products.only_active().filter(is_available=False).count()

    @property
    def products_with_variations(self) -> int:
        return self.products.only_active().filter(is_available__isnull=True).count()

    @property
    def products_not_active(self) -> int:
        return self.products.filter(is_active=False).count()

    @property
    def is_affiliated(self) -> bool:
        return bool(self.affiliate_query_param and self.affiliate_id)



class ShippingMethod(BaseModel):
    store = models.ForeignKey(
        Store, related_name="shipping_methods", on_delete=models.CASCADE
    )
    name = models.CharField("Name", max_length=128)
    min_shipping_time = models.SmallIntegerField(
        "Minimum Shipping Time in days", default=1
    )
    max_shipping_time = models.SmallIntegerField(
        "Maximum Shipping Time in days", null=True, blank=True
    )
    price = models.DecimalField(
        "Shipping Cost", null=True, blank=True, max_digits=5, decimal_places=2
    )
    currency = models.CharField(
        "Default Currency", max_length=3, choices=Store.CURRENCIES, default="EUR"
    )
    min_price_shipping_condition = models.DecimalField(
        "Minimum price to get this shipping",
        null=True,
        blank=True,
        max_digits=5,
        decimal_places=2,
    )
    shipping_zone = models.ForeignKey(
        "ShippingZone",
        null=True,
        blank=True,
        related_name="shipping_methods",
        on_delete=models.SET_NULL
    )
    is_vat_included = models.BooleanField(
        "Is VAT included?",
        default=True
    )
    is_weight_dependent = models.BooleanField(
        "Does the price depend on the shipping weight?",
        default=False
    )

    @property
    def is_free(self) -> bool:
        return not bool(self.price) and not self.is_weight_dependent

    def __str__(self):
        return self.display_name

    @property
    def display_name(self) -> str:
        return f"{self.store.name} - {self.name}"


class SuggestedShippingMethod(BaseModel):
    store = models.ForeignKey(
        Store, related_name="suggested_shipping_methods", on_delete=models.CASCADE
    )
    name = models.CharField("Name", max_length=128)
    price = models.DecimalField(
        "Shipping Cost", null=True, blank=True, max_digits=5, decimal_places=2
    )
    min_price_shipping_condition = models.DecimalField(
        "Minimum price to get this shipping",
        null=True,
        blank=True,
        max_digits=5,
        decimal_places=2,
    )
    is_weight_dependent = models.BooleanField(
        "Does the price depend on the shipping weight?",
        default=False
    )

    def __str__(self):
        return f"Suggestion for {self.store} - {self.name}"

class Brand(BaseModel):
    name = models.CharField("Name of the brand", max_length=64)
    description = models.TextField("Description")
    logo = models.ImageField("Brand Logo")
    is_hot = models.BooleanField("Is an hot brand?", default=False)

    def __str__(self):
        return self.name


class ImportQuery(BaseModel):
    """This model is used to import a product"""
    PRIORITY_LOW = 0
    PRIORITY_MEDIUM = 1
    PRIORITY_HIGH = 2
    PRIORITY_CHOICES = (
        (PRIORITY_LOW, "Low"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_HIGH, "High"),
    )

    text = models.CharField("The text to search on the stores", max_length=256)
    priority = models.IntegerField("Import Priority", choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    products_clicks = models.IntegerField("Clicks of the imported products", default=0)
    priority_score = models.FloatField("Priority Score", default=PRIORITY_MEDIUM)
    brand = models.ForeignKey(Brand, related_name="import_queries", on_delete=models.DO_NOTHING, null=True, blank=True)

    class Meta:
        verbose_name = "Import Query"
        verbose_name_plural = "Import Queries"
        ordering = ("-priority_score",)

    def __str__(self):
        return f"{self.text} ({self.get_priority_display()})"

    def update_priority_score(self, commit=True):
        self.products_clicks += 1
        self.priority_score = self.priority + self.products_clicks / 100

        if commit:
            self.save(update_fields=["products_clicks", "priority_score"])

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.update_priority_score(commit=False)
        super().save(force_insert, force_update, using, update_fields)


class ProductQuerySet(QuerySet):
    def only_active(self):
        return self.filter(is_active=True)

class Product(BaseModel):
    """This model represent the base class for a generic product"""

    id = models.CharField("Unique ID", max_length=770, primary_key=True)

    name = models.CharField("The name of the product", max_length=512)
    description = models.TextField("Description of the product")
    price = models.FloatField("Price of the product")
    currency = models.CharField("Currency", default="USD", max_length=3)
    review = models.FloatField("The average stars from reviews", null=True, blank=True)
    image = models.URLField("The url of the product's image", null=True, max_length=1024)
    link = models.URLField("The url of the product's page", default="", max_length=1024)
    store = models.ForeignKey(Store, related_name="products", on_delete=models.CASCADE)

    is_available = models.BooleanField(
        "Is available", default=True, null=True, blank=True
    )
    import_date = models.DateTimeField("Import date", auto_now=True, auto_created=True)
    import_query = models.ForeignKey(
        ImportQuery,
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )
    brand = models.ForeignKey(Brand, related_name="products", on_delete=models.DO_NOTHING, null=True, blank=True)

    search_vector = SearchVectorField(null=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        indexes = [GinIndex(fields=["search_vector"])]

    def __str__(self):
        return f"{self.name} from {self.store.name}, price: {self.price}"

    @property
    def click_score(self) -> int:
        return self.clicks.count()

    @property
    def best_shipping_method(self) -> ShippingMethod:
        free_shipping = self.store.shipping_methods.filter(
            price__isnull=True, min_price_shipping_condition__isnull=False
        )
        if not free_shipping.exists():
            return self.store.best_shipping_method()

        free_shipping = free_shipping.first()

        if self.price >= free_shipping.min_price_shipping_condition:
            return free_shipping

        return self.store.best_shipping_method()

    @property
    def affiliate_link(self):
        if not self.store.is_affiliated:
            return self.link

        url_parts = list(urlparse(self.link))
        query = dict(parse_qsl(url_parts[4]))
        query[self.store.affiliate_query_param] = self.store.affiliate_id
        url_parts[4] = urlencode(query)

        return urlunparse(url_parts)


class Continent(BaseModel):
    name = models.CharField("The name of the continent", max_length=128)

    def __str__(self):
        return self.name


class Country(BaseModel):
    name = models.CharField("The name of the country", max_length=128)
    continent = models.ForeignKey(Continent, related_name="countries", on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


class ShippingZone(BaseModel):
    name = models.CharField("The name of the shipping zone", max_length=128)
    ship_to = models.ManyToManyField(Country)

    def __str__(self):
        return self.name


class ClickedProductQuerySet(QuerySet):
    def created_after(self, after_date: timezone) -> QuerySet:
        return self.filter(
            created_at__gte=after_date
        )

class ClickedProduct(BaseModel):
    product = models.ForeignKey(Product, null=True, related_name="clicks", on_delete=models.SET_NULL)
    clicked_after_seconds = models.FloatField("Clicked After Seconds")
    search_query = models.CharField("Search query", max_length=512)
    page = models.IntegerField("Result page")

    objects = ClickedProductQuerySet.as_manager()

    class Meta:
        verbose_name_plural = "Clicked Products"

    def __str__(self):
        return f"Clicked {self.product.name}"

    @property
    def store(self):
        return self.product.store

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.pk and self.product.import_query:
            self.product.import_query.update_priority_score()
        super().save(force_insert, force_update, using, update_fields)


class RequestedStore(BaseModel):
    website = models.URLField("URL of the store")
    is_spam = models.BooleanField("Is Spam", default=False)
    is_already_present = models.BooleanField("Is the store already present")

    def __str__(self):
        return f"Request for {self.website} {'(Already requested)' if self.is_already_present else ''}"
