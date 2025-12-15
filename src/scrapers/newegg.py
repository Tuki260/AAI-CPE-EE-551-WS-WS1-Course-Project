# scrapers/newegg.py
import re
import gzip
from urllib.error import HTTPError
from http.cookiejar import CookieJar
from urllib.request import Request, build_opener, HTTPCookieProcessor

class NeweggScrapeError(Exception):
    """Raised when Newegg data cannot be extracted."""

class NeweggScraper:
    def __init__(self, timeout: int = 20, user_agent: str | None = None):
        self.timeout = timeout
        self.cookie_jar = CookieJar()
        self.opener = build_opener(HTTPCookieProcessor(self.cookie_jar))
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36")

    def _fetch_html(self, url: str) -> str:
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
            with self.opener.open(req, timeout=self.timeout) as resp:
                raw = resp.read()
                encoding = (resp.headers.get("Content-Encoding") or "").lower()
        except HTTPError as e:
            raise NeweggScrapeError(f"HTTP {e.code}: Forbidden by Newegg") from e

        if "gzip" in encoding:
            raw = gzip.decompress(raw)
        return raw.decode("utf-8", errors="replace")

    def get_price_currency(self, html: str):
        # print(html)
        m = re.search(r'"price"\s*:\s*"([0-9]+(?:\.[0-9]+)?)"\s*,\s*"priceCurrency"\s*:\s*"([A-Z]{3})"', html)

        if not m:
            return None, None
        return float(m.group(1)), m.group(2)
        
    def get_brand(self, html: str):
        m = re.search(r'Key=\\"Brand\\"\s+Value=\\"([^\\"]+)\\\"', html)
        if m:
            return m.group(1)
        else:
            return None

    # def get_series(self, html: str):
    #     m = re.search(r'Key=\\"Series\\"\s+Value=\\"([^\\"]+)\\\"', html)
    #     if m:
    #         return m.group(1)
    #     else:
    #         return None

    def get_model(self, html: str):
        m = re.search(r'"brand"\s*:\s*"([^"]+)"[\s\S]*?"(?:model|Model|mpn)"\s*:\s*"([^"]+)"', html)

        if m:
            return m.group(2)
        else:
            return None

    def scrape_data(self, url: str):
        html = self._fetch_html(url)
        
        brand = self.get_brand(html)
        model = self.get_model(html)
        # series = self.get_series(html)
        price, currency = self.get_price_currency(html)
        if price is not None and currency and brand and (model or series):
            return price, currency, brand, model#, series

        raise NeweggScrapeError("Could not find a reliable price on the Newegg page.")


if __name__ == "__main__":
    scraper = NeweggScraper()
    # url = "https://www.newegg.com/g-skill-trident-z5-rgb-series-32gb-ddr5-6000-cas-latency-cl36-desktop-memory-black/p/N82E16820374351?Item=N82E16820374351"
    url = "https://www.newegg.com/g-skill-ripjaws-m5-neo-rgb-series-32gb-ddr5-6000-cas-latency-cl36-desktop-memory-black/p/N82E16820374642?Item=N82E16820374642"
    # url = "https://www.newegg.com/asus-b650e-max-gaming-wifi-w-atx-motherboard-amd-b650-am5/p/N82E16813119736"
    price, currency, brand, model, series = scraper.scrape_data(url)
    print(f"Price: {price}\nCurrency: {currency}\nBrand: {brand}\nModel: {model}\nSeries: {series}")