from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """The base model that every other model should extends"""

    created_at = models.DateTimeField(auto_now=True, auto_created=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Store(BaseModel):
    """This model represent an online store"""

    CURRENCIES = (("EUR", "Euro"), ("USD", "US Dollar"))

    LOCALE = (("en_US", "American"), ("it_IT", "European"))

    name = models.CharField("Name of the store", max_length=256)
    website = models.URLField("URL of the store")
    country = models.ForeignKey("Country", related_name="stores", null=True, default=None, on_delete=models.SET_NULL)
    locale = models.CharField(
        "Locale used in the store",
        max_length=5,
        choices=LOCALE,
        default="it_IT",
        help_text="If the store uses , as decimal separator choose European",
    )
    currency = models.CharField(
        "Default Currency", max_length=3, choices=CURRENCIES, default="EUR"
    )
    last_check = models.DateTimeField("Last check", null=True)

    is_scrapable = models.BooleanField("Is the store still compatible?", default=False)
    is_scrapable.short_description = "Is the store still compatible?"
    is_scrapable.boolean = True

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

    product_name_class = models.CharField(
        "The css class of the product's name", max_length=64
    )
    product_name_tag = models.CharField(
        "The html tag of the product's name", max_length=64
    )
    product_price_class = models.CharField(
        "The css class of the product's price", max_length=64
    )
    product_price_tag = models.CharField(
        "The html tag of the product's price", max_length=64
    )
    product_image_class = models.CharField(
        "The css class of the main image of the product",
        max_length=64,
        null=True,
        blank=True,
    )
    product_image_tag = models.CharField(
        "The html tag of the main image of the product",
        max_length=64,
        null=True,
        blank=True,
    )
    product_thumb_class = models.CharField(
        "The css class of the thumbnail images of the product",
        max_length=64,
        null=True,
        blank=True,
    )
    product_thumb_tag = models.CharField(
        "The html tag of the thumbnail images of the product",
        max_length=64,
        null=True,
        blank=True,
    )
    product_is_available_class = models.CharField(
        "The css class to know if the product is available",
        max_length=64,
        null=True,
        blank=True,
    )
    product_is_available_tag = models.CharField(
        "The html tag to know if the product is available",
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
        "The css class to know if the product has variations",
        max_length=64,
        null=True,
        blank=True,
    )
    product_variations_tag = models.CharField(
        "The html tag to know if the product has variations",
        max_length=64,
        null=True,
        blank=True,
    )
    product_description_class = models.CharField(
        "The css class to know if the product description",
        max_length=64,
        null=True,
        blank=True,
    )
    product_description_tag = models.CharField(
        "The html tag to know if the product description",
        max_length=64,
        null=True,
        blank=True,
    )

    def __str__(self):
        return "{} ({})".format(
            self.name,
            self.website,
        )

    def set_is_not_scarpable(self, reason: str):
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
        return self.shipping_methods.filter(price__isnull=False).order_by("price").first()

    @property
    def imported_products(self) -> int:
        return self.products.count()

    @property
    def products_in_stock(self) -> int:
        return self.products.filter(is_available=True).count()

    @property
    def products_out_of_stock(self) -> int:
        return self.products.filter(is_available=False).count()

    @property
    def products_with_variations(self) -> int:
        return self.products.filter(is_available__isnull=True).count()


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
    min_price_shipping_condition = models.DecimalField(
        "Minimum price to get this shipping",
        null=True,
        blank=True,
        max_digits=5,
        decimal_places=2,
    )
    shipping_rule = models.ForeignKey(
        "ShippingRule",
        null=True,
        blank=True,
        related_name="shipping_methods",
        on_delete=models.SET_NULL
    )

    @property
    def is_free(self):
        return self.price is None or self.price == 0

    def __str__(self):
        return f"{self.store.name} - {self.name}"


class Category(BaseModel):
    """This model represent a the category of a product"""

    name = models.CharField("The name of the category", max_length=256)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


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

    def __str__(self):
        return "{} from {}, price: {}".format(
            self.name,
            self.store.name,
            self.price,
        )

    @property
    def click_score(self):
        return self.clicks.count()


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


class ShippingRule(BaseModel):
    name = models.CharField("The name of the shipping rule", max_length=128)
    ship_to = models.ManyToManyField(Country)


class ClickedProduct(BaseModel):
    product = models.ForeignKey(Product, null=True, related_name="clicks", on_delete=models.SET_NULL)
    clicked_after_seconds = models.FloatField("Clicked After Seconds")
    search_query = models.CharField("Search query", max_length=512)
    page = models.IntegerField("Result page")

    class Meta:
        verbose_name_plural = "Clicked Products"

    def __str__(self):
        return f"Clicked {self.product.name}"


class RequestedStore(BaseModel):
    website = models.URLField("URL of the store")
    is_spam = models.BooleanField("Is Spam", default=False)
    is_already_present = models.BooleanField("Is the store already present")

    def __str__(self):
        return f"Request for {self.website} {'(Already requested)' if self.is_already_present else ''}"
