# scrapers/microcenter.py
import requests
import re

class MicrocenterScrapeError(Exception):
    """Raised when Microcenter data cannot be extracted."""

class MicrocenterScraper:
    """
    MicrocenterScraper class

    This class is used to scrape product data from links that lead to microcenter.com.
    It gets data like price, currency, brand, and model.

    We use regular expressions to look at the html and find the data we want.
    """

    def __init__(self, timeout: int = 20):
        """
        Initialize the MicrocenterScraper objects.
        
        timeout (int): Maximum number of seconds to wait for an HTTP response before timing out.
        """
        self.timeout = timeout

    def get_price_currency(self, html: str):
        """
        Extract the product price and currency from the HTML.

        html (str): Raw HTML content of the Microcenter product page.

        Returns:
            tuple: (price, currency) where price is a float and currency
                   is a string. Returns (None, None) if
                   values cannot be found.
        """
        price = None
        currency = None

        m = re.search(r"'productPrice'\s*:\s*'([\d,]+(?:\.\d+)?)'", html)
        if m:
            price = float(m.group(1).replace(",", ""))

        m = re.search(r'"priceCurrency"\s*:\s*"([A-Z]{3})"', html)
        if m:
            currency = m.group(1)

        return price, currency

    def get_brand(self, html: str):
        """
        Extract the product brand from the HTML.

        html (str): Raw HTML content of the Microcenter product page.

        Returns:
            str: Brand name if found, otherwise None.
        """
        m = re.search(r"'brand'\s*:\s*'([^']+)'", html)
        return m.group(1) if m else None

    def get_model(self, html: str):
        """
        Extract the product model number (MPN) from the HTML.

        html (str): Raw HTML content of the Microcenter product page.

        Returns:
            str: Model number if found, otherwise None.
        """
        m = re.search(r"'mpn'\s*:\s*'([^']+)'", html)
        return m.group(1) if m else None

    def scrape_data(self, product_url: str):
        """
        Scrape product data from a Microcenter product URL.

        This method performs an HTTP GET request, extracts the
        HTML content, and parses the price, currency, brand,
        and model information by calling the other methods.

        product_url (str): URL of the Microcenter page.

        Returns:
            tuple: (price, currency, brand, model)

        If any required data cannot be found, it raises the MicrocenterScrapeError exception
        """
        r = requests.get(product_url, timeout=self.timeout)
        html = r.text

        price, currency = self.get_price_currency(html)
        brand = self.get_brand(html)
        model = self.get_model(html)

        if price and currency and brand and model:
            return price, currency, brand, model

        raise MicrocenterScrapeError("Could not find a reliable price on the Microcenter page.")


if __name__ == "__main__":
    scraper = MicrocenterScraper()
    url = "https://www.microcenter.com/product/688526/corsair-vengeance-rgb-32gb-(2-x-16gb)-ddr5-6000-pc5-48000-cl36-dual-channel-desktop-memory-kit-cmh32gx5m2m6000z36-black"
    price, currency, brand, model = scraper.scrape_data(url)
    print(f"Price: {price}\nCurrency: {currency}\nBrand: {brand}\nModel: {model}")
