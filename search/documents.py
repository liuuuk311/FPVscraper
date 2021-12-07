from django_elasticsearch_dsl import (
    Document,
    fields,
    Index,
)
from elasticsearch_dsl import analyzer

from .models import Product, Store


product_index = Index('products')

product_index.settings(
    number_of_shards=1,
    number_of_replicas=0
)

html_strip = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)


@product_index.document
class ProductDocument(Document):
    store = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(),
        'best_shipping_method': fields.ObjectField(properties={
            'name_en': fields.TextField(),
            'name_it': fields.TextField(),
            'min_shipping_time': fields.IntegerField(),
            'price': fields.FloatField(),
            'is_free': fields.BooleanField(),
            'min_price_shipping_condition': fields.FloatField(),
        })
    })
    name = fields.TextField(
        attr='name',
        fields={
            'suggest': fields.Completion(),
            'raw': fields.KeywordField(),
        }
    )
    description = fields.TextField(
        attr='description',
        analyzer=html_strip,
        fields={
            'raw': fields.KeywordField(),
        }
    )
    is_available = fields.BooleanField(
        attr='is_available',
        fields={
            'raw': fields.BooleanField(),
        }
    )

    click_score = fields.IntegerField(
        attr='click_score',
        fields={
            'raw': fields.IntegerField(),
        }
    )

    class Django:
        model = Product
        fields = [
            'id',
            'price',
            'currency',
            'image',
            'link',
        ]

        related_models = [Store]

    def get_instances_from_related(self, related_instance):
        """If related_models is set, define how to retrieve the Product instance(s) from the related model.
        The related_models option should be used with caution because it can lead in the index
        to the updating of a lot of items.
        """
        if isinstance(related_instance, Store):
            return related_instance.products.all()