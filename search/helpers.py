import random
from threading import Thread
from time import sleep
from typing import Dict

from celery.utils.log import get_task_logger
from django.db.models import QuerySet
from django.db.utils import IntegrityError
from django.utils import timezone
from requests import TooManyRedirects

from helpers.logger import logger
from scraper.simple import scrape_product, search
from search.models import Product, Store, ImportQuery

celery_logger = get_task_logger(__name__)


def create_or_update_product(store: Store, data: Dict, query: ImportQuery) -> bool:
    if not data:
        return False


    product_id = f"{store.name}_{data.get('name')}".replace(' ', '_')
    celery_logger.info(f"ID: {product_id}")
    data["store"] = store
    data['import_date'] = timezone.now()
    data['import_query'] = query
    data['brand'] = query.brand if query.brand and query.brand.name in data.get("name", "") else None
    data.pop("variations", None)
    celery_logger.info(f"Product data to create: {data}")
    try:
        product, created = Product.objects.update_or_create(id=product_id, defaults=data)
    except IntegrityError as e:
        qs = Product.objects.filter(id=product_id)
        if qs.exists():
            product = qs.first()
            product.is_active = False
            product.save(update_fields=["is_active"])
        return False

    return bool(created)


def random_sleep_time() -> float:
    return random.uniform(1.5, 4.5)


def re_import_products_from(store_qs: QuerySet):
    threads = []
    for store in store_qs:
        p = Thread(target=re_import_store_products, args=(store,))
        p.start()
        threads.append(p)

    for t in threads:
        t.join()


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
        logger.warning(f'{store} is not compatible. Import cancelled')
        return

    for product in store.products.only_active().order_by("import_date"):
        logger.info(f"Re importing {product.name} from {product.store.name}")
        try:
            import_product(product.link, product.store, product.import_query)
        except (ConnectionError, TooManyRedirects):
            product.is_active = False
            product.save(update_fields=["is_active"])

    store.last_check = timezone.now()
    store.save(update_fields=["last_check"])


def search_and_import_products(query: ImportQuery, store: Store):
    if not store.is_scrapable:
        logger.warning(f'{store} is not compatible. Import cancelled')
        return

    urls = search(query.text, store, limit=None)
    for url in urls:
        import_product(url, store, query)

    store.last_check = timezone.now()
    store.save(update_fields=["last_check"])


def search_and_import_from(store_qs: QuerySet):
    for query in ImportQuery.objects.filter(is_active=True):
        processes = []
        for store in store_qs:
            p = Thread(target=search_and_import_products, args=(query, store))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()