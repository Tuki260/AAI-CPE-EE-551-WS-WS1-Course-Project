# scrapers/newegg.py
import re
import gzip
from urllib.error import HTTPError, URLError
from http.cookiejar import CookieJar
from urllib.request import Request, build_opener, HTTPCookieProcessor
from socket import timeout as SocketTimeout

class NeweggScrapeError(Exception):
    """Raised when Newegg data cannot be extracted."""

class NeweggScraper:
    """
    NeweggScraper class

    This class is used to scrape product data from links that lead to newegg.com.
    It gets data like price, currency, brand, and model.

    We use regular expressions to look at the html and find the data we want. 
    The scraper uses HTTP headers and cookies to mimic a real browser session in order to reduce the likelihood of being blocked.
    """

    def __init__(self, timeout: int = 20, user_agent: str | None = None):
        """
        Initialize the NeweggScraper objects.

        timeout (int): Maximum number of seconds to wait for a server
                        response before timing out.
        user_agent (str): Optional custom User-Agent string.
                          If one is not given, a default desktop browser User-Agent is used.
        """

        self.timeout = timeout
        # Cookie jar helps maintain a browser-like session
        self.cookie_jar = CookieJar()
        self.opener = build_opener(HTTPCookieProcessor(self.cookie_jar))
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36")

    def _fetch_html(self, url: str) -> str:
        """
        Fetch the raw HTML from a Newegg product page.
        """
        # Browser-like headers reduce blocking
        headers = {
            "User-Agent": self.user_agent,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.newegg.com/",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "close",
            "Upgrade-Insecure-Requests": "1",
        }

        req = Request(url, headers=headers)

        try:
            # Attempt to fetch page HTML
            with self.opener.open(req, timeout=self.timeout) as resp:
                raw = resp.read()
                encoding = (resp.headers.get("Content-Encoding") or "").lower()

        except HTTPError as e:
            # HTTP errors such as 403 or 404
            raise NeweggScrapeError(
                f"HTTP {e.code} fetching Newegg URL: {url}"
            ) from e
        except (URLError, SocketTimeout) as e:
            # Network or timeout issues
            raise NeweggScrapeError(
                f"Network/timeout error fetching Newegg URL: {url}"
            ) from e
        except Exception as e:
            # Last-resort safety net
            raise NeweggScrapeError(
                f"Unexpected error fetching Newegg URL: {url}"
            ) from e

        # Decompress gzip responses if required
        if "gzip" in encoding:
            try:
                raw = gzip.decompress(raw)
            except Exception:
                # Fallback if decompression fails
                pass

        # Decode HTML for regex processing
        return raw.decode("utf-8", errors="replace")


    def get_price_currency(self, html: str):
        """
        Extract the product price and currency from the HTML.

        html (str): Raw HTML content of the Newegg page.

        Returns:
            tuple: (price, currency) where price is a float and currency
                   is a string.
        """

        m = re.search(r'"price"\s*:\s*"([0-9]+(?:\.[0-9]+)?)"\s*,\s*"priceCurrency"\s*:\s*"([A-Z]{3})"', html)

        if not m:
            return None, None
        return float(m.group(1)), m.group(2)
        
    def get_brand(self, html: str):
        """
        Extract the product brand from the HTML.

        html (str): Raw HTML content of the Newegg page.

        Returns:
            str: Brand name if found, otherwise None.
        """

        m = re.search(r'Key=\\"Brand\\"\s+Value=\\"([^\\"]+)\\\"', html)
        if m:
            return m.group(1)
        else:
            return None

    def get_model(self, html: str):
        """
        Extract the product model number from the HTML.

        html (str): Raw HTML content of the Newegg page.

        Returns:
            str: Model number if found, otherwise None.
        """

        m = re.search(r'"brand"\s*:\s*"([^"]+)"[\s\S]*?"(?:model|Model|mpn)"\s*:\s*"([^"]+)"', html)

        if m:
            return m.group(2)
        else:
            return None

    def scrape_data(self, url: str):
        """
        Scrape product data from a Newegg product URL.

        This method coordinates HTML retrieval and data extraction,
        ensuring all required fields are present before returning
        results. It calls the class' other methods to get the needed data.

        url (str): Newegg product page URL.

        Returns:
            tuple: (price, currency, brand, model)

        If any required data cannot be found, it raises the NeweggScrapeError exception
        """

        html = self._fetch_html(url)
        #Get individual data from the HTML
        brand = self.get_brand(html)
        model = self.get_model(html)
        # series = self.get_series(html)
        price, currency = self.get_price_currency(html)
        # All fields are required for a valid result
        if price is not None and currency and brand and model:
            return price, currency, brand, model#, series

        raise NeweggScrapeError("Could not find a reliable price on the Newegg page.")


if __name__ == "__main__":
    scraper = NeweggScraper()
    # url = "https://www.newegg.com/g-skill-trident-z5-rgb-series-32gb-ddr5-6000-cas-latency-cl36-desktop-memory-black/p/N82E16820374351?Item=N82E16820374351"
    url = "https://www.newegg.com/g-skill-ripjaws-m5-neo-rgb-series-32gb-ddr5-6000-cas-latency-cl36-desktop-memory-black/p/N82E16820374642?Item=N82E16820374642"
    # url = "https://www.newegg.com/asus-b650e-max-gaming-wifi-w-atx-motherboard-amd-b650-am5/p/N82E16813119736"
    price, currency, brand, model = scraper.scrape_data(url)
    print(f"Price: {price}\nCurrency: {currency}\nBrand: {brand}\nModel: {model}")