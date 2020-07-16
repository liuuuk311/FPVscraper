import unicodedata
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup


def get_soup(url):
    """ Get a soup object from a url """
    # TODO: implement checks on the urls validity and respose status code

    page = requests.get(url)
    return BeautifulSoup(page.content, 'html.parser')


def scrape_product(url, config):
    """
    Scrape a product from a url based on the config dict

    :param url: a valid product page to scrape
    :param config: a dictionary with field names as keys.
        Each field must have two keys: tag and class

    :returns: a dictionary with fields as given in the config and values scraped.
        If a field is not found in the page, it won't be returned.
    """

    soup = get_soup(url)

    data = {}
    for field in config:
        style_class = config[field]['class']
        html_tag = config[field]['tag']
        soup_obj = soup.find(html_tag, class_=style_class)
        if soup_obj:
            unicode_str = soup_obj.get_text()
            data[field] = unicodedata.normalize("NFKD", unicode_str).strip()

    return data


def search(query, config, limit=1):
    """
    Search for the given query on a store and returns a list of product pages

    :param query: a string of the product we are looking for
    :param config: a dictionary with a search object.
        'search': {
            'url':   ...,  # This represent the base url of the search page
            'tag':   ...,  # This represent the html tag of each product item displayed in the result page
            'class': ...,  # This represent the css class of the tag above
            'link':  ...,  # This represent the css class from where to search the product page link
        },
    :param limit: (optional) the maximum number of results

    :return: a list of product pages
    """
    url = config['search']['url'] + query
    soup = get_soup(url)

    style_class = config['search']['class']
    html_tag = config['search']['tag']
    soup_list = soup.find_all(name=html_tag, attrs={'class': style_class}, limit=limit)

    urls = []
    link_tag = config['search']['link']
    for obj in soup_list:
        title = obj.find(class_=link_tag)
        if title:
            href = title.find_next('a')['href']
            if href.startswith('/'):
                href = config['base'] + href

            urls.append(href)

    return urls


if __name__ == '__main__':

    # GetFPV
    getfpv = {
        'base': 'http://www.getfpv.com',
        'search': {
            'url': 'http://www.getfpv.com/catalogsearch/result/?q=',  # This represent the base url of the search page
            'tag': 'li',  # This represent the html tag of each product item displayed in the result page
            'class': 'item',  # This represent the css class of the tag above
            'link': 'product-name',  # This represent the css class from where to search the product page link
        },
        'product': {
            # Info needed to scrape a product
            'name': {'class': 'product-name', 'tag': 'div'},
            'price': {'class': 'price', 'tag': 'span'},
            'stars': {'class': 'sr-only', 'tag': 'span'},
            'description': {'class': 'tab-content', 'tag': 'div'},
        }
    }

    # RaceDayQuad
    rdq = {
        'base': 'http://www.racedayquads.com',
        'search': {
            'url': 'http://www.racedayquads.com/search?type=product&q=',
            # This represent the base url of the search page
            'tag': 'div',  # This represent the html tag of each product item displayed in the result page
            'class': 'productitem',  # This represent the css class of the tag above
            'link': 'productitem--title'  # This represent the css class from where to search the product page link
        },
        'product': {
            # Info needed to scrape a product
            'name': {'class': 'product-title', 'tag': 'h1'},
            'price': {'class': 'price--main', 'tag': 'div'},
            'stars': {'class': 'yotpo-starsd ', 'tag': 'span'},
            'description': {'class': 'tab-content', 'tag': 'span'},
        }

    }

    query_text = quote('T motor f40 pro IV')

    getfpv_urls = search(query_text, getfpv)
    for product_url in getfpv_urls:
        print(scrape_product(product_url, getfpv['product']))

    rdq_urls = search(query_text, rdq)
    for product_url in rdq_urls:
        print(scrape_product(product_url, rdq['product']))
