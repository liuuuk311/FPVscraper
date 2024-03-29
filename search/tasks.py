import requests
from celery.task import task
from requests.exceptions import ConnectionError, TooManyRedirects

from helpers.logger import logger
from scraper.simple import search, scrape_product, get_random_user_agent
from search.helpers import (
    re_import_store_products,
    re_import_products_from,
    import_product,
    search_and_import_from
)
from search.models import Store, Product


@task(name='check_scraping_compatibility')
def check_scraping_compatibility(store_pk: int) -> bool:
    config = Store.objects.get(pk=store_pk)
    logger.info(f"Starting to check compatibility for {config.name}")
    # Is the store still available?
    try:
        headers = {'User-Agent': get_random_user_agent()}
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
        logger.info(urls)
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


@task(name='search_and_import_store_products')
def task_search_and_import_store_products(store_pk):
    search_and_import_from(Store.objects.filter(pk=store_pk))


@task(name='re_import_product')
def task_re_import_product(product_id: str):
    product = Product.objects.get(id=product_id)
    try:
        import_product(product.link, product.store, product.import_query)
    except TooManyRedirects:
        product.is_active = False
        product.save(update_fields=["is_active"])

@task(name="re_import_product_from_store")
def task_re_import_product_from_store(store_pk: int):
    re_import_store_products(store_pk)


@task(name="search_and_import_products_from_active_stores")
def task_search_and_import_products_from_active_stores():
    search_and_import_from(Store.objects.only_active())
    logger.info("Search and import done for  stores", send_to_telegram=True)


@task(name="search_and_import_products_from_asian_stores")
def task_search_and_import_products_from_asian_stores():
    search_and_import_from(Store.objects.only_asian())
    logger.info("Search and import done for asian stores", send_to_telegram=True)


@task(name="search_and_import_products_from_european_stores")
def task_search_and_import_products_from_european_stores():
    search_and_import_from(Store.objects.only_european())
    logger.info("Search and import done for european stores", send_to_telegram=True)


@task(name="search_and_import_products_from_american_stores")
def task_search_and_import_products_from_american_stores():
    search_and_import_from(Store.objects.only_american())
    logger.info("Search and import done for america stores", send_to_telegram=True)


@task(name="search_and_import_products_from_australia_stores")
def task_search_and_import_products_from_australia_stores():
    search_and_import_from(Store.objects.only_australian())
    logger.info("Search and import done for australian stores", send_to_telegram=True)


@task(name="re_import_product_from_active_stores")
def task_re_import_product_from_active_stores():
    re_import_products_from(Store.objects.only_active())
    logger.info("Reimport done for active stores", send_to_telegram=True)


@task(name="re_import_products_from_asian_stores")
def task_re_import_products_from_asian_stores():
    re_import_products_from(Store.objects.only_asian())
    logger.info("Reimport done for asian stores", send_to_telegram=True)


@task(name="re_import_products_from_european_stores")
def task_re_import_products_from_european_stores():
    re_import_products_from(Store.objects.only_european())
    logger.info("Reimport done for european stores", send_to_telegram=True)


@task(name="re_import_products_from_american_stores")
def task_re_import_products_from_american_stores():
    re_import_products_from(Store.objects.only_american())
    logger.info("Reimport done for american stores", send_to_telegram=True)


@task(name="re_import_products_from_australian_stores")
def task_re_import_products_from_australian_stores():
    re_import_products_from(Store.objects.only_australian())
    logger.info("Reimport done for australian stores", send_to_telegram=True)
