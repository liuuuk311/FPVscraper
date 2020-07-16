from django.db import models


class BaseModel(models.Model):
    """ The base model that every other model should extends """

    created_at = models.DateTimeField(auto_now=True, auto_created=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Store(BaseModel):
    """ This model represent an online store """

    REGIONS = (
        ('USA', 'United States'),
        ('ITA', 'Italy'),
        ('CHN', 'China'),
        ('OTH', 'Other')
    )

    name = models.CharField("The name of the store", max_length=256)
    website = models.URLField("The URL of the store")
    region = models.CharField("The region of the store", max_length=3, choices=REGIONS)
    last_check = models.DateTimeField("The timestamp of the last check")

    def __str__(self):
        return "{} ({})".format(
            self.name,
            self.website,
        )


class Category(BaseModel):
    """ This model represent a the category of a product """

    name = models.CharField("The name of the category", max_length=256)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Product(BaseModel):
    """ This model represent the base class for a generic product """

    name = models.CharField("The name of the product", max_length=512)
    description = models.TextField("Description of the product")
    price = models.FloatField("Price of the product")
    average_stars = models.FloatField("The average stars from reviews", null=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return "{} from {}, price: {}".format(
            self.name,
            self.store.name,
            self.price,
        )


class Picture(BaseModel):
    """ This model represent an online picture """

    url = models.URLField("The url of the picture")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        class_name = type(self).__name__
        return "[{}]: {}".format(
            class_name,
            self.url,
        )


