import re
import gzip
from urllib.error import HTTPError
from http.cookiejar import CookieJar
from urllib.request import Request, build_opener, HTTPCookieProcessor


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
        self.cookie_jar = CookieJar()
        self.opener = build_opener(HTTPCookieProcessor(self.cookie_jar))
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

    def _fetch_html(self, url: str) -> str:
        """
        Fetch the raw HTML from a ShopBLT product page.
        This method sends an HTTP request with browser-like headers.

        url (str): shopblt product URL.

        Returns:
            str: HTML content of the page.

        If ShopBLT blocks the request, the ShopBLTScrapeError exception is raised
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
            with self.opener.open(req, timeout=self.timeout) as resp:
                raw = resp.read()
                encoding = (resp.headers.get("Content-Encoding") or "").lower()
        except HTTPError as e:
            raise ShopBLTScrapeError(f"HTTP {e.code}: Error fetching ShopBLT page") from e
        
        if "gzip" in encoding:
            try:
                raw = gzip.decompress(raw)
            except Exception:
                pass

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

        m = re.search(
            r'Your(?:\s|&nbsp;)*Price\s*:\s*(?:</?\w+[^>]*>\s*)*\$([0-9,]+\.\d{2})',
            html,
            flags=re.IGNORECASE
        )
        if not m:
            m = re.search(
                r'Your(?:\s|&nbsp;)*Price[^$]*\$([0-9,]+\.\d{2})',
                html,
                flags=re.IGNORECASE
            )
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

        patterns = [
            r'Manufacturer\s*:\s*(?:</?\w+[^>]*>\s*)*Mfg\.\s*:\s*(?:</?\w+[^>]*>\s*)*([^<\n\r]+)',
            r'Manufacturer\s*:\s*(?:</?\w+[^>]*>\s*)*([^<\n\r]+)',
            r'\bMfg\.\s*:\s*(?:</?\w+[^>]*>\s*)*([^<\n\r]+)',
        ]
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

        patterns = [
            r'Mfg\.\s*Part\s*#\s*:\s*(?:</?\w+[^>]*>\s*)*([A-Za-z0-9._/-]+)',
            r'Mfg\s*Part\s*#\s*:\s*(?:</?\w+[^>]*>\s*)*([A-Za-z0-9._/-]+)',
            r'\bPart\s*#\s*:\s*(?:</?\w+[^>]*>\s*)*([A-Za-z0-9._/-]+)',
        ]
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

        price, currency = self.get_price_currency(html)
        brand = self.get_brand(html)
        model = self.get_model(html)

        if price is not None and currency:
            return price, currency, brand, model

        raise ShopBLTScrapeError("Could not find a reliable price on the shopBLT page.")


if __name__ == "__main__":
    scraper = ShopBLTScraper()
    #url = "https://www.shopblt.com/cgi-bin/shop/shop.cgi?action=thispage&thispage=01100300U031_BYS0258P.shtml&order_id=198503165"
    #url = "https://www.shopblt.com/cgi-bin/shop/shop.cgi?action=thispage&thispage=01100500U011_B6TZ187P.shtml&order_id=198503165"
    url = "https://www.shopblt.com/cgi-bin/shop/shop.cgi?action=thispage&thispage=011003501501_B6QC407P.shtml&order_id=198503165"
    price, currency, brand, model, blt_item = scraper.scrape_shopblt(url)
    print(f"Price: {price}\nCurrency: {currency}\nBrand: {brand}\nModel: {model}\nBLT Item: {blt_item}")
