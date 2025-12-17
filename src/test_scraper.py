import pytest
from scrapers.mainScraper import mainScraper

# pytest -v -s test_scraper.py

class TestMainScraper:
    def setup_method(self):
        self.scraper = mainScraper()

    def test_newegg_product(self):
        url = "https://www.newegg.com/g-skill-ripjaws-m5-neo-rgb-series-32gb-ddr5-6000-cas-latency-cl36-desktop-memory-black/p/N82E16820374642?Item=N82E16820374642"
        price, currency, brand, model = self.scraper.scrape_product(url)

        assert price == 359.99
        assert currency == "USD"
        assert brand == "G.SKILL"
        assert model is not None

    def test_microcenter_product(self):
        url = "https://www.microcenter.com/product/688526/corsair-vengeance-rgb-32gb-(2-x-16gb)-ddr5-6000-pc5-48000-cl36-dual-channel-desktop-memory-kit-cmh32gx5m2m6000z36-black"
        price, currency, brand, model = self.scraper.scrape_product(url)

        assert price == 409.99
        assert currency == "USD"
        assert brand == "Corsair"
        assert model is not None

    def test_shopblt_product(self):
        url = "https://www.shopblt.com/cgi-bin/shop/shop.cgi?action=thispage&thispage=011003501501_B6QC407P.shtml&order_id=198503165"
        price, currency, brand, model = self.scraper.scrape_product(url)

        assert price == 37.05
        assert currency == "USD"
        assert brand == "4XEM"
        assert model is not None
