# scrapers/newegg.py
import re
# from dataclasses import dataclass
from urllib.request import Request, urlopen

class NeweggScrapeError(Exception):
    """Raised when Newegg data cannot be extracted."""

def _fetch_html(url: str, timeout: int = 20) -> str:
    req = Request(url)
    with urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    return raw.decode("utf-8", errors="replace")

def get_price_currency(html: str):
    # print(html)
    m = re.search(
    r'"price"\s*:\s*"([0-9]+(?:\.[0-9]+)?)"\s*,\s*"priceCurrency"\s*:\s*"([A-Z]{3})"',
    html
    )

    if m:
        price = float(m.group(1))
        currency = m.group(2)
        return price, currency
    
def get_brand(html: str):
    m = re.search(r'Key=\\"Brand\\"\s+Value=\\"([^\\"]+)\\\"', html)
    if m:
        brand = m.group(1)
        # print(brand)
        return brand

def get_series(html: str):
    m = re.search(r'Key=\\"Series\\"\s+Value=\\"([^\\"]+)\\\"', html)
    if m:
        series = m.group(1)
        # print(series)
        return series

def get_model(html: str):
    m = re.search(
    r'"brand"\s*:\s*"([^"]+)"[\s\S]*?"(?:model|Model|mpn)"\s*:\s*"([^"]+)"',
    html,
    flags=re.IGNORECASE
    )

    if m:
        brand = m.group(1)
        model = m.group(2)
        # print(model)
        return model

def scrape_newegg_price(url: str):
    """
    Scrape a product price from a Newegg product URL.
    Returns ScrapeResult(price, currency) or raises NeweggScrapeError.
    """
    html = _fetch_html(url)
    
    brand = get_brand(html)
    model = get_model(html)
    series = get_series(html)
    price, currency = get_price_currency(html)
    if price and currency and brand and (model or series):
        return price, currency, brand, model, series

    raise NeweggScrapeError("Could not find a reliable price on the Newegg page.")


if __name__ == "__main__":
    # url = "https://www.newegg.com/g-skill-trident-z5-rgb-series-32gb-ddr5-6000-cas-latency-cl36-desktop-memory-black/p/N82E16820374351?Item=N82E16820374351"
    url = "https://www.newegg.com/g-skill-ripjaws-m5-neo-rgb-series-32gb-ddr5-6000-cas-latency-cl36-desktop-memory-black/p/N82E16820374642?Item=N82E16820374642"
    # url = "https://www.newegg.com/asus-b650e-max-gaming-wifi-w-atx-motherboard-amd-b650-am5/p/N82E16813119736"
    price, currency, brand, model, series = scrape_newegg_price(url)
    print(f"Price: {price}\nCurrency: {currency}\nBrand: {brand}\nModel: {model}\nSeries: {series}")