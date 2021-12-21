from datetime import datetime
from threading import Thread
from time import sleep

import requests
from requests.exceptions import ConnectionError
from celery.task import task

from scraper.simple import search, scrape_product
from search.helpers import create_or_update_product
from helpers.logger import logger
from search.models import Store, ImportQuery, Product


@task(name='check_scraping_compatibility')
def check_scraping_compatibility(store_pk: int) -> bool:
    config = Store.objects.get(pk=store_pk)
    logger.info(f"Starting to check compatibility for {config.name}")
    # Is the store still available?
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        res = requests.get(config.website, headers=headers)
        if res.status_code == 503:
            config.scrape_with_js = True
            config.save(update_fields=["scrape_with_js"])
        elif res.status_code != 200:
            config.set_is_not_scrapable(f'Cannot reach {config.website} status code was: {res.status_code}')
            return False
    except ConnectionError:
        config.set_is_not_scrapable(f'Cannot reach {config.website} because of connection error')
        return False

    logger.info("OK: We can reach the website")

    product_pages = []
    # Can we perform some query?
    queries = ['Motor', 'ESC']
    for query in queries:
        urls = search(query, config)
        if not urls:
            config.set_is_not_scrapable(f'The search for {query} did not produced any url')
            return False
        else:
            product_pages.append(urls[0])

    logger.info(f"OK: We can perform queries, got {len(product_pages)} to check")

    for product_page in product_pages:
        data = scrape_product(product_page, config)
        if not data.get("name"):
            config.set_is_not_scrapable(f'Could not find a name for the product at {product_page}')
            return False

        if not data.get("price"):
            config.set_is_not_scrapable(f'Could not find a price for the product at {product_page}')
            return False
        logger.info(f"Scraped {data}")

    config.set_is_scrapable()
    logger.info("{} is compatible with the scraping".format(config.name))
    return True


@task(name='import_products_from_import_queries')
def import_products_from_import_queries(store_pk):
    config = Store.objects.get(pk=store_pk)
    if not config.is_scrapable:
        logger.warning('{} is not compatible. Import cancelled'.format(config))
        return

    start = datetime.now()
    for query in ImportQuery.objects.filter(is_active=True):
        logger.info("Importing {} from {}".format(query, config.name))
        import_products(query, config)
        sleep(5)

    elapsed = datetime.now() - start
    logger.info("Imported new products for {} in ".format(config.name, str(elapsed)), send_to_telegram=True)
    config.last_check = datetime.now()
    config.save(update_fields=["last_check"])


def import_products(query: ImportQuery, config: Store, delay: float = 5):
    urls = search(query.text, config, limit=None)
    for url in urls:
        data = scrape_product(
            url, config, fields=['name', 'price', 'image', 'is_available', 'variations', 'description']
        )
        created = create_or_update_product(config, data, query)
        if created:
            sleep(delay)


@task(name='re_import_product')
def re_import_product(product_id: str):
    product = Product.objects.get(id=product_id)
    _re_import_product(product)


def _re_import_product(product: Product):
    logger.info(f"Re importing {product.name} from {product.store.name}")
    data = scrape_product(
        product.link, product.store, fields=['name', 'price', 'image', 'is_available', 'variations', 'description']
    )
    create_or_update_product(product.store, data, product.import_query)


@task(name="import_all_products_for_all_stores")
def import_all_products_for_all_stores():
    start = datetime.now()
    for query in ImportQuery.objects.filter(is_active=True):
        processes = []
        for store in Store.objects.filter(is_active=True):
            p = Thread(target=import_products, args=(query, store))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

    elapsed = datetime.now() - start
    logger.info("Imported new and old products in ".format(str(elapsed)), send_to_telegram=True)


@task(name="re_import_all_products")
def re_import_all_products():
    start = datetime.now()
    threads = []
    for store in Store.objects.filter(is_active=True):
        if len(threads) == 5:
            threads[0].join()

        p = Thread(target=_re_import_product_from_store, args=(store, ))
        p.start()
        threads.append(p)

    for t in threads:
        t.join()

    elapsed = datetime.now() - start
    logger.info("Re imported ALL products in ".format(str(elapsed)), send_to_telegram=True)


def _re_import_product_from_store(store: Store):
    for product in store.products.order_by("import_date"):
        _re_import_product(product)
        sleep(2)


@task(name="re_import_product_from_store")
def re_import_product_from_store(store_pk: int):
    store = Store.objects.get(pk=store_pk)
    _re_import_product_from_store(store)
