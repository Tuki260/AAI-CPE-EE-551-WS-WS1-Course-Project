import re
import gzip
from urllib.error import HTTPError, URLError
from http.cookiejar import CookieJar
from urllib.request import Request, build_opener, HTTPCookieProcessor
from socket import timeout as SocketTimeout


class ShopBLTScrapeError(Exception):
    """Raised when ShopBLT data cannot be extracted."""


class ShopBLTScraper:
    """
    ShopBLTScraper class

    This class is used to scrape product data from links that lead to shopblt.com.
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
        self.cookie_jar = CookieJar() # Cookie jar helps maintain session like a real browser
        self.opener = build_opener(HTTPCookieProcessor(self.cookie_jar))
        # Reduces blocking by using realistic user-agent headers later in the code
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

    def _fetch_html(self, url: str) -> str:
        """
        Fetch the raw HTML from a ShopBLT product page.
        """
        headers = {
            "User-Agent": self.user_agent,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.shopblt.com/",
            "Connection": "close",
            "Upgrade-Insecure-Requests": "1",
            "Accept-Encoding": "gzip, deflate",
        }

        req = Request(url, headers=headers)

        try:
            # Attempt to fetch page HTML
            with self.opener.open(req, timeout=self.timeout) as resp:
                raw = resp.read()
                encoding = (resp.headers.get("Content-Encoding") or "").lower()

        except HTTPError as e:
            # HTTP errors such as 403 or 404
            raise ShopBLTScrapeError(f"HTTP {e.code} fetching ShopBLT URL: {url}") from e
        except (URLError, SocketTimeout) as e:
            # Network or timeout issues
            raise ShopBLTScrapeError(f"Network/timeout error fetching ShopBLT URL: {url}") from e
        except Exception as e:
            # Last-resort safety net
            raise ShopBLTScrapeError(f"Unexpected error fetching ShopBLT URL: {url}") from e

        # Decompress gzip content if needed
        if "gzip" in encoding:
            try:
                raw = gzip.decompress(raw)
            except Exception:
                # If decompression fails, fall back to raw bytes
                pass

        # Decode HTML so it can be parsed with regex
        return raw.decode("utf-8", errors="replace")

    def _clean(self, s: str):
        """
        Fixes up scraped text by removing whitespaces and other unneeded chars.

        s (str): Raw extracted string.

        Returns:
            str: Cleaned string with normalized spacing.
        """

        return re.sub(r"\s+", " ", s.replace("&nbsp;", " ")).strip()

    def get_price_currency(self, html: str):
        """
        Extract the product price and currency from the HTML.

        html (str): Raw HTML content of the ShopBLT page.

        Returns:
            tuple: (price, currency) where price is a float and currency is a string.
        """
        # Attempt multiple patterns to handle ShopBLT page variations
        m = re.search(r'Your(?:\s|&nbsp;)*Price\s*:\s*(?:</?\w+[^>]*>\s*)*\$([0-9,]+\.\d{2})', html, flags=re.IGNORECASE)
        if not m:
            m = re.search(r'Your(?:\s|&nbsp;)*Price[^$]*\$([0-9,]+\.\d{2})', html, flags=re.IGNORECASE)
        if not m:
            return None, None

        price = float(m.group(1).replace(",", ""))
        return price, "USD"

    def get_brand(self, html: str):
        """
        Extract the product brand from the HTML.

        html (str): Raw HTML content of the ShopBLT page.

        Returns:
            str: Brand name if found, otherwise None.
        """
        # Multiple patterns are used again to handle different page layouts
        patterns = [r'Manufacturer\s*:\s*(?:</?\w+[^>]*>\s*)*Mfg\.\s*:\s*(?:</?\w+[^>]*>\s*)*([^<\n\r]+)', r'Manufacturer\s*:\s*(?:</?\w+[^>]*>\s*)*([^<\n\r]+)', r'\bMfg\.\s*:\s*(?:</?\w+[^>]*>\s*)*([^<\n\r]+)']
        for pat in patterns:
            m = re.search(pat, html, flags=re.IGNORECASE)
            if m:
                return self._clean(m.group(1))
        return None

    def get_model(self, html: str):
        """
        Extract the product model number from the HTML.

        html (str): Raw HTML content of the ShopBLT page.

        Returns:
            str: Model number if found, otherwise None.
        """
        # Again test different patters to account for the different formats of shopBLT
        patterns = [r'Mfg\.\s*Part\s*#\s*:\s*(?:</?\w+[^>]*>\s*)*([A-Za-z0-9._/-]+)', r'Mfg\s*Part\s*#\s*:\s*(?:</?\w+[^>]*>\s*)*([A-Za-z0-9._/-]+)', r'\bPart\s*#\s*:\s*(?:</?\w+[^>]*>\s*)*([A-Za-z0-9._/-]+)']
        for pat in patterns:
            m = re.search(pat, html, flags=re.IGNORECASE)
            if m:
                return self._clean(m.group(1))
        return None

    def scrape_data(self, url: str):
        """
        Scrape product data from a ShopBLT product URL.

        This method coordinates HTML retrieval and data extraction,
        ensuring all required fields are present before returning
        results. It calls the class' other methods to get the needed data.

        url (str): shopblt product page URL.

        Returns:
            tuple: (price, currency, brand, model)

        If any required data cannot be found, it raises the ShopBLTScrapeError exception
        """

        html = self._fetch_html(url)
        #extraplolating data from the HTML
        price, currency = self.get_price_currency(html)
        brand = self.get_brand(html)
        model = self.get_model(html)

        if price is not None and currency:
            return price, currency, brand, model

        raise ShopBLTScrapeError("Could not find a reliable price on the shopBLT page.")


if __name__ == "__main__":
    scraper = ShopBLTScraper()
    #url = "https://www.shopblt.com/cgi-bin/shop/shop.cgi?action=thispage&thispage=01100300U031_BYS0258P.shtml&order_id=198503165"
    url = "https://www.shopblt.com/cgi-bin/shop/shop.cgi?action=thispage&thispage=01100500U011_B6TZ187P.shtml&order_id=198503165"
    #url = "https://www.shopblt.com/cgi-bin/shop/shop.cgi?action=enter&thispage=011003000507_BKS1078P.shtml"
    price, currency, brand, model = scraper.scrape_data(url)
    print(f"Price: {price}\nCurrency: {currency}\nBrand: {brand}\nModel: {model}")
