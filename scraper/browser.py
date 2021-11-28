from selenium import webdriver


def get_html(url: str) -> str:
    driver = webdriver.PhantomJS()
    driver.get(url)
    html = driver.page_source
    driver.close()
    return html