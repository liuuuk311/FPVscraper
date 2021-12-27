import random
from datetime import datetime
from threading import Thread
from time import sleep
from typing import Dict

import elasticsearch
from celery.utils.log import get_task_logger
from django.db.models import QuerySet
from django.db.utils import DataError, IntegrityError
from django.utils import timezone

from helpers.logger import logger
from scraper.simple import scrape_product, search
from search.models import Product, Store, ImportQuery

celery_logger = get_task_logger(__name__)


def create_or_update_product(store: Store, data: Dict, query: ImportQuery) -> bool:
    if not data:
        return False

    product_id = "{}_{}".format(store.name, data.get('name')).replace(' ', '_')
    celery_logger.info(f"ID: {product_id}")
    data["store"] = store
    data['import_date'] = timezone.now()
    data['import_query'] = query
    data.pop("variations", None)
    celery_logger.info(f"Product data to create: {data}")
    try:
        product, created = Product.objects.update_or_create(id=product_id, defaults=data)
    except IntegrityError as e:
        celery_logger.error(f"Could not create or update: {data['link']}")
        product = Product.objects.filter(id=product_id)
        if product.exists():
            product.is_active = False
            product.save(update_fields=["is_active"])
        return False
    except elasticsearch.exceptions.ConnectionError as e:
        celery_logger.error(f"Product not created, Elasticsearch is probably down, waiting for it to restart. Error: {e}")
        sleep(20)
        return False

    return bool(created)


def random_sleep_time() -> float:
    return random.uniform(1.5, 4.5)


def re_import_products_from(store_qs: QuerySet):
    start = datetime.now()
    threads = []
    for store in store_qs:
        p = Thread(target=re_import_store_products, args=(store,))
        p.start()
        threads.append(p)

    for t in threads:
        t.join()

    elapsed = datetime.now() - start
    logger.info("Re imported ALL products in ".format(str(elapsed)), send_to_telegram=True)


def import_product(link: str, store: Store, import_query: ImportQuery):
    data = scrape_product(
        link, store, fields=['name', 'price', 'image', 'is_available', 'variations', 'description']
    )
    created = create_or_update_product(store, data, import_query)
    if created:
        sleep(random_sleep_time())


def re_import_store_products(store: Store):
    """ Re import all products of a given store """
    if not store.is_scrapable:
        logger.warning('{} is not compatible. Import cancelled'.format(store))
        return

    for product in store.products.order_by("import_date"):
        logger.info(f"Re importing {product.name} from {product.store.name}")
        import_product(product.link, product.store, product.import_query)

    store.last_check = timezone.now()
    store.save(update_fields=["last_check"])


def search_and_import_products(query: ImportQuery, store: Store):
    if not store.is_scrapable:
        logger.warning('{} is not compatible. Import cancelled'.format(store))
        return

    urls = search(query.text, store, limit=None)
    for url in urls:
        import_product(url, store, query)

    store.last_check = timezone.now()
    store.save(update_fields=["last_check"])


def search_and_import_from(store_qs: QuerySet):
    start = datetime.now()
    for query in ImportQuery.objects.filter(is_active=True):
        processes = []
        for store in store_qs:
            p = Thread(target=search_and_import_products, args=(query, store))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

    elapsed = datetime.now() - start
    logger.info("Imported new and old products in ".format(str(elapsed)), send_to_telegram=True)