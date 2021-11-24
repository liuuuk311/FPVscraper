from typing import Dict

from celery.utils.log import get_task_logger
from django.db.utils import DataError
from django.utils import timezone

from search.models import Product, Store

logger = get_task_logger(__name__)


def create_or_update_product(store: Store, data: Dict) -> bool:
    product_id = "{}_{}".format(store.name, data.get('name').replace(' ', '_'))
    logger.info(f"ID: {product_id}")
    data["store"] = store
    data['import_date'] = timezone.now()
    logger.info(f"Product data to create: {data}")
    try:
        product, created = Product.objects.update_or_create(id=product_id, defaults=data)
    except DataError as e:
        logger.error(f"Product not created. Error: {e}")
        return False

    return bool(created)
