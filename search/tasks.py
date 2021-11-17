from datetime import datetime
from threading import Thread
from time import sleep

import requests
from requests.exceptions import ConnectionError
from celery.task import task
from celery.utils.log import get_task_logger

from scraper import search, scrape_product
from search.helpers import create_or_update_product
from search.models import Store, Category, Product

logger = get_task_logger(__name__)


@task(name='check_scraping_compatibility')
def check_scraping_compatibility(store_pk: int) -> bool:
    config = Store.objects.get(pk=store_pk)
    logger.info(f"Starting to check compatibility for {config.name}")
    # Is the store still available?
    try:
        res = requests.get(config.website)
        if res.status_code != 200:
            config.set_is_not_scarpable(f'Cannot reach {config.website} status code was: {res.status_code}')
            return False
    except ConnectionError:
        config.set_is_not_scarpable(f'Cannot reach {config.website} because of connection error')
        return False

    logger.info("OK: We can reach the website")

    product_pages = []
    # Can we perform some query?
    queries = ['Motor', 'ESC', 'Goggles']
    for query in queries:
        urls = search(query, config, limit=1)
        if not urls:
            config.set_is_not_scarpable(f'The search for {query} did not produced any url')
            return False
        else:
            product_pages.append(urls[0])

    logger.info(f"OK: We can perform queries, got {len(product_pages)} to check")

    for product_page in product_pages:
        data = scrape_product(product_page, config)
        if 'name' not in data:
            config.set_is_not_scarpable(f'Could not find a name for the product at {product_page}')
            return False

        if 'price' not in data:
            config.set_is_not_scarpable(f'Could not find a price for the product at {product_page}')
            return False

    config.set_is_scrapable()
    logger.info("{} is compatible with the scraping".format(config.name))
    return True


@task(name='import_products_from_categories')
def import_products_from_categories(store_pk):
    config = Store.objects.get(pk=store_pk)
    if not config.is_scrapable:
        logger.warning('{} is not compatible. Import cancelled'.format(config))
        return

    categories = Category.objects.filter(is_active=True)
    threads = []

    start = datetime.now()
    for category in categories:
        logger.info("Importing {} from {}".format(category, config.name))
        thread = Thread(target=import_products, args=(category.name, config))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    elapsed = datetime.now() - start
    logger.info("Imported new products for {} in ".format(config.name, str(elapsed)))


def import_products(category: str, config: Store, delay: float = 0.5):
    urls = search(category, config, limit=None)
    for url in urls:
        data = scrape_product(url, config, fields=['name', 'price', 'image', 'is_available', 'variations'])
        created = create_or_update_product(config, data)
        if created:
            sleep(delay)

@task(name='re_import_product')
def re_import_product(product_id: int):
    product = Product.objects.get(id=product_id)
    data = scrape_product(product.link, product.store, fields=['name', 'price', 'image', 'is_available', 'variations'])
    create_or_update_product(product.store, data)




