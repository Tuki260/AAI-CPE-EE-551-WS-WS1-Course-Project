# scrapers/microcenter.py
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from socket import timeout as SocketTimeout


class MicrocenterScrapeError(Exception):
    """Raised when Microcenter data cannot be extracted."""


class MicrocenterScraper:
    """
    MicrocenterScraper class

    This class is used to scrape product data from links that lead to microcenter.com.
    It gets data like price, currency, brand, and model.

    We use regular expressions to look at the html and find the data we want.
    """

    def __init__(self, timeout: int = 20, user_agent: str | None = None):
        """
        Initialize the MicrocenterScraper object.

        timeout (int): Maximum number of seconds to wait for a server
                       response before timing out.
        user_agent (str): Optional custom User-Agent string.
                          If one is not given, a default desktop browser User-Agent is used.
        """
        self.timeout = timeout
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

    def _fetch_html(self, url: str) -> str:
        """
        Fetch the raw HTML from a Microcenter product page.
        """
        headers = {
            "User-Agent": self.user_agent,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.microcenter.com/",
            "Connection": "close",
            "Upgrade-Insecure-Requests": "1",
        }

        req = Request(url, headers=headers)

        try:
            with urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read()

                # If server provides a charset, we use it otherwise we default to utf-8.
                content_type = resp.headers.get("Content-Type", "")
                m = re.search(r"charset=([^\s;]+)", content_type, re.I)
                encoding = m.group(1) if m else "utf-8"

        except HTTPError as e:
            raise MicrocenterScrapeError(f"HTTP {e.code} fetching Microcenter URL: {url}") from e
        except (URLError, SocketTimeout) as e:
            raise MicrocenterScrapeError(f"Network/timeout error fetching Microcenter URL: {url}") from e
        except Exception as e:
            # last-resort catch so our program doesn't hard-crash
            raise MicrocenterScrapeError(f"Unexpected error fetching Microcenter URL: {url}") from e

        try:
            return raw.decode(encoding, errors="replace")
        except LookupError:
            # unknown encoding name -> fallback
            return raw.decode("utf-8", errors="replace")

    def get_price_currency(self, html: str):
        """
        Extract the product price and currency from the HTML.

        Returns:
            tuple: (price, currency)
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
        """
        m = re.search(r"'brand'\s*:\s*'([^']+)'", html) # Look for the product price value in embedded page data
        return m.group(1) if m else None

    def get_model(self, html: str):
        """
        Extract the product model number (MPN) from the HTML.
        """
        m = re.search(r"'mpn'\s*:\s*'([^']+)'", html) # MPN is used as a unique model identifier
        return m.group(1) if m else None

    def scrape_data(self, url: str):
        """
        Scrape product data from a Microcenter product URL.

        Returns:
            tuple: (price, currency, brand, model)

        Raises:
            MicrocenterScrapeError
        """
        html = self._fetch_html(url)
        # Extract individual data fields from the HTML
        price, currency = self.get_price_currency(html)
        brand = self.get_brand(html)
        model = self.get_model(html)

        if price is not None and currency and brand and model:
            return price, currency, brand, model
        # Raise an error if parsing the data failed
        raise MicrocenterScrapeError("Could not find a reliable price on the Microcenter page.")


if __name__ == "__main__":
    scraper = MicrocenterScraper()
    #url = "https://www.microcenter.com/product/688526/corsair-vengeance-rgb-32gb-(2-x-16gb)-ddr5-6000-pc5-48000-cl36-dual-channel-desktop-memory-kit-cmh32gx5m2m6000z36-black"
    url = "https://www.microcenter.com/product/688526/corsair-vengeance-rgb-32gb-(2-x-16gb)-ddr5-6000-pc5-48000-cl36-dual-channel-desktop-memory-kit-cmh32gx5m2m6000z36-black"

    price, currency, brand, model = scraper.scrape_data(url)
    print(f"Price: {price}\nCurrency: {currency}\nBrand: {brand}\nModel: {model}")

