import pytest
from scrapers.mainScraper import mainScraper

# pytest -v -s test_scraper.py

class TestMainScraper:
    """
    3 Tests for the mainScraper class.

    These tests verify that mainScraper correctly selects the appropriate
    website-specific scraper and successfully extracts product data.

    These tests rely on live websites. Prices may
    change over time, which can cause assertions to fail even if the
    scraping logic is correct.
    """

    def setup_method(self):
        """
        Create a mainScraper instance before each test.
        """

        self.scraper = mainScraper()

    def test_newegg_product(self):
        """
        Test scraping a known Newegg product URL.
        """

        url = "https://www.newegg.com/g-skill-ripjaws-m5-neo-rgb-series-32gb-ddr5-6000-cas-latency-cl36-desktop-memory-black/p/N82E16820374642?Item=N82E16820374642"
        price, currency, brand, model = self.scraper.scrape_product(url)

        assert price == 359.99
        assert currency == "USD"
        assert brand == "G.SKILL"
        assert model is not None

    def test_microcenter_product(self):
        """
        Test scraping a known Microcenter product URL.
        """

        url = "https://www.microcenter.com/product/688526/corsair-vengeance-rgb-32gb-(2-x-16gb)-ddr5-6000-pc5-48000-cl36-dual-channel-desktop-memory-kit-cmh32gx5m2m6000z36-black"
        price, currency, brand, model = self.scraper.scrape_product(url)

        assert price == 409.99
        assert currency == "USD"
        assert brand == "Corsair"
        assert model is not None

    def test_shopblt_product(self):
        """
        Test scraping a known ShopBLT product URL.
        """

        url = "https://www.shopblt.com/cgi-bin/shop/shop.cgi?action=thispage&thispage=011003501501_B6QC407P.shtml&order_id=198503165"
        price, currency, brand, model = self.scraper.scrape_product(url)

        assert price == 37.05
        assert currency == "USD"
        assert brand == "4XEM"
        assert model is not None
