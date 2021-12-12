from asyncio import sleep
from typing import Dict

import elasticsearch
from celery.utils.log import get_task_logger
from django.db.utils import DataError, IntegrityError
from django.utils import timezone

from search.models import Product, Store, ImportQuery

logger = get_task_logger(__name__)


def create_or_update_product(store: Store, data: Dict, query: ImportQuery) -> bool:
    if not data:
        return False

    product_id = "{}_{}".format(store.name, data.get('name')).replace(' ', '_')
    logger.info(f"ID: {product_id}")
    data["store"] = store
    data['import_date'] = timezone.now()
    data['import_query'] = query
    data.pop("variations", None)
    logger.info(f"Product data to create: {data}")
    try:
        product, created = Product.objects.update_or_create(id=product_id, defaults=data)
    except (DataError, IntegrityError) as e:
        logger.error(f"Product not created. Error: {e}")
        return False
    except elasticsearch.exceptions.ConnectionError as e:
        logger.error(f"Product not created, Elasticsearch is probably down, waiting for it to restart. Error: {e}")
        sleep(20)
        return False

    return bool(created)
