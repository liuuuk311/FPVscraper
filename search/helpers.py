from typing import Dict

from django.utils import timezone

from search.models import Product, Store


def create_or_update_product(store: Store, data: Dict) -> bool:
    product_id = "{}_{}".format(store.name, data.get('name').replace(' ', '_'))
    data["store"] = store
    data['import_date'] = timezone.now()
    product, created = Product.objects.update_or_create(id=product_id, defaults=data)
    return bool(created)