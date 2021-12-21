import locale
import re

import random
import unicodedata
from time import sleep
from typing import Optional, List, Dict
from urllib.parse import quote

import requests
import urllib
from bs4 import BeautifulSoup
from celery.utils.log import get_task_logger

from scraper.browser import get_html
from search.models import Store

logger = get_task_logger(__name__)


def get_soup(url: str, js_enabled: bool = False) -> Optional[BeautifulSoup]:
    """ Get a soup object from a url """
    if js_enabled:
        logger.info("Getting HTML through a browser in order to use JS")
        html = get_html(url)
    else:
        page = requests.get(url, headers={'User-Agent': get_random_user_agent()})
        if page.status_code != 200:
            return None
        html = page.content

    return BeautifulSoup(html, 'html.parser')


def get_link(soup: BeautifulSoup, config: Store) -> str:
    href = soup.find_next('a')['href']
    if href.startswith('/'):
        href = config.website + href
    return href


def format_image_link(text: str) -> str:
    text = text.format(width=300)
    if text.startswith("//"):
        text = f"https:{text}"
    return text


def parse_price(price_string: str, store_locale: str = "it_IT") -> Optional[float]:
    regex = r"(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2}))"
    pattern = re.compile(regex)
    match = pattern.match(price_string.strip("€").strip("$"))
    if match:
        locale.setlocale(locale.LC_NUMERIC, store_locale)
        return locale.atof(match.group(1))
    return None


def scrape_product(url: str, config: Store, fields: Optional[List[str]] = None) -> Dict:
    """
    Scrape a product from a url based on the config dict

    :param url: a valid product page to scrape
    :param config: a search.models.Store instance.
    :param fields: (optional) a list of fields in search.models.Store

    :returns: a dictionary with fields as given in the config and values scraped.
        If a field is not found in the page, it won't be returned.
    """
    fields = fields or ['name', 'price', 'image']

    logger.info(f"Looking for {fields} on {url}")
    soup = get_soup(url, js_enabled=config.scrape_with_js)
    data = {}

    if not soup:
        return data

    for field in fields:
        style_class = getattr(config, "product_{}_class".format(field))
        html_tag = getattr(config, "product_{}_tag".format(field))

        if not bool(style_class) or not bool(html_tag):
            continue

        soup_obj = soup.find(html_tag, class_=style_class)

        logger.info(f"Scraping {field} with tag {html_tag} and class {style_class}")

        if field == 'is_available' and 'is_available' not in data:
            logger.info(f"Found {soup_obj.get_text() if soup_obj else 'nothing'}")
            data[field] = bool(re.search(config.product_is_available_match, soup_obj.get_text())) if soup_obj else False
            continue

        if soup_obj:
            unicode_str_text = soup_obj.get_text()
            logger.info(f"Found {unicode_str_text.strip()}")

            if field == 'image':
                if soup_obj.name != "img":
                    soup_obj = soup_obj.find("img")
                img_link = soup_obj['data-src'] if soup_obj.has_attr('data-src') else soup_obj['src']
                data[field] = format_image_link(img_link)

            elif field == 'price':
                price = parse_price(unicode_str_text.strip(), store_locale=config.locale)
                data[field] = price
                data['currency'] = config.currency

            elif field == 'variations' and not data.get("is_available", None):
                data['is_available'] = None
            else:
                data[field] = unicodedata.normalize("NFKD", unicode_str_text).strip()

    data['link'] = url
    return data


def search(query: str, config: Store, limit: Optional[int] = 1, seconds_of_sleep: int = 10) -> List[str]:
    """
    Search for the given query on a store and returns a list of product pages

    :param query: a string of the product we are looking for
    :param config: a search.models.Store instance.
    :param limit: (optional) the maximum number of results,
        if None return all possible products looping through the pages
    :param seconds_of_sleep: (optional) number of seconds of sleep between scraping pages

    :return: a list of scraped urls
    """
    next_url = config.search_url + quote(query)
    scraped_urls = []

    while next_url:
        logger.info(f"Searching {query} at {next_url}")
        soup = get_soup(next_url, js_enabled=config.scrape_with_js)
        if not soup:
            return scraped_urls

        next_url = None

        soup_list = soup.find_all(name=config.search_tag,
                                  attrs={'class': config.search_class},
                                  limit=limit)

        for obj in soup_list:
            title = obj.find(class_=config.search_link)
            if title:
                href = get_link(title, config)

                if limit and len(scraped_urls) == limit:
                    return scraped_urls

                scraped_urls.append(href)

        if not config.search_next_page:
            return scraped_urls
            
        next_link = soup.find(class_=config.search_next_page)

        if next_link:
            if next_link.name != "a":
                next_link = next_link.find("a")
            
            next_url = next_link['href']
            if next_url and not next_url.startswith("http"):
                next_url = urllib.parse.urljoin(config.website, next_url)
            sleep(seconds_of_sleep)

    return scraped_urls


def get_random_user_agent():
    agents = [
        "Mozilla/5.0 (X11; Linux ppc64le; rv:75.0) Gecko/20100101 Firefox/75.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/75.0",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:75.0) Gecko/20100101 Firefox/75.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A",
        "Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2919.83 Safari/537.36",
        "Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
    ]
    return random.choice(agents)
