from django_elasticsearch_dsl import (
    Document,
    fields,
    Index,
)
from elasticsearch_dsl import analyzer, token_filter

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

edge_ngram_completion_filter = token_filter(
    'edge_ngram_completion_filter',
    type="edge_ngram",
    min_gram=1,
    max_gram=20
)


edge_ngram_completion = analyzer(
    "edge_ngram_completion",
    tokenizer="standard",
    filter=["lowercase", edge_ngram_completion_filter]
)


@product_index.document
class ProductDocument(Document):
    store = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(
            fields={
                'raw': fields.KeywordField(),
            }
        ),
        'country': fields.ObjectField(properties={
            'id': fields.IntegerField(),
            'continent': fields.ObjectField(properties={
                'id':  fields.IntegerField()
            })
        })
    })
    name = fields.TextField(
        attr='name',
        fields={
            'suggest': fields.CompletionField(),
            'edge_ngram_completion': fields.TextField(
                analyzer=edge_ngram_completion
            ),
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

    affiliate_link = fields.TextField(
        attr='affiliate_link',
    )

    best_shipping_method = fields.ObjectField(properties={
        'name_en': fields.TextField(),
        'name_it': fields.TextField(),
        'min_shipping_time': fields.IntegerField(),
        'price': fields.FloatField(),
        'is_free': fields.BooleanField(),
        'min_price_shipping_condition': fields.FloatField(),
    })

    class Django:
        model = Product
        fields = [
            'id',
            'price',
            'currency',
            'image',
        ]

        related_models = [Store]

    def get_instances_from_related(self, related_instance):
        """If related_models is set, define how to retrieve the Product instance(s) from the related model.
        The related_models option should be used with caution because it can lead in the index
        to the updating of a lot of items.
        """
        if isinstance(related_instance, Store):
            return related_instance.products.all()