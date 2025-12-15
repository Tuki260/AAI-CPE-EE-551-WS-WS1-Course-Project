# scrapers/microcenter.py
import requests
import re

class MicrocenterScrapeError(Exception):
    """Raised when Microcenter data cannot be extracted."""

def get_price_currency(html: str):
    price = None
    currency = None

    m = re.search(r"'productPrice'\s*:\s*'([\d,]+(?:\.\d+)?)'", html)
    if m:
        price = float(m.group(1).replace(",", ""))

    m = re.search(r'"priceCurrency"\s*:\s*"([A-Z]{3})"', html)
    if m:
        currency = m.group(1)

    return price, currency


def get_brand(html: str):
    m = re.search(r"'brand'\s*:\s*'([^']+)'", html)
    return m.group(1) if m else None


def get_model(html: str):
    m = re.search(r"'mpn'\s*:\s*'([^']+)'", html)
    return m.group(1) if m else None


def scrape_microcenter(product_url: str):

    r = requests.get(product_url)
    # r.raise_for_status()
    html = r.text

    price, currency = get_price_currency(html)
    brand = get_brand(html)
    model = get_model(html)

    if price and currency and brand and model:
        return price, currency, brand, model

    raise MicrocenterScrapeError("Could not find a reliable price on the Microcenter page.")


if __name__ == "__main__":
    url = "https://www.microcenter.com/product/688526/corsair-vengeance-rgb-32gb-(2-x-16gb)-ddr5-6000-pc5-48000-cl36-dual-channel-desktop-memory-kit-cmh32gx5m2m6000z36-black"
    price, currency, brand, model = scrape_microcenter(url)
    print(f"Price: {price}\nCurrency: {currency}\nBrand: {brand}\nModel: {model}")
