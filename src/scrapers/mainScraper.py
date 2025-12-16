from . import microcenter, newegg, shopblt

class mainScraper:
    def __init__(self):
        self.scrapers = {
            "microcenter.com": microcenter.MicrocenterScraper(),
            "newegg.com": newegg.NeweggScraper(),
            "shopblt.com": shopblt.ShopBLTScraper(),
        }

    def determine_website(self, url: str):
        if "microcenter.com" in url:
            return "microcenter.com"
        elif "newegg.com" in url:
            return "newegg.com"
        elif "shopblt.com" in url:
            return "shopblt.com"
        else:
            pass # Website not supported

    def determine_scraper(self, url):
        domain = self.determine_website(url)

        if domain in self.scrapers:
            return self.scrapers[domain]

    def scrape_product(self, url):
        scraper = self.determine_scraper(url)

        if hasattr(scraper, "scrape_data"):
            price, currency, brand, model = scraper.scrape_data(url)

        return price, currency, brand, model

if __name__ == "__main__":
    scraper = mainScraper()
    # url = "https://www.microcenter.com/product/688526/corsair-vengeance-rgb-32gb-(2-x-16gb)-ddr5-6000-pc5-48000-cl36-dual-channel-desktop-memory-kit-cmh32gx5m2m6000z36-black"
    # url = "https://www.newegg.com/g-skill-ripjaws-m5-neo-rgb-series-32gb-ddr5-6000-cas-latency-cl36-desktop-memory-black/p/N82E16820374642?Item=N82E16820374642"
    url = "https://www.shopblt.com/cgi-bin/shop/shop.cgi?action=thispage&thispage=011003501501_B6QC407P.shtml&order_id=198503165"
    # scraper.scrape_product(url)
    price, currency, brand, model = scraper.scrape_product(url)
    print(f"Price: {price}\nCurrency: {currency}\nBrand: {brand}\nModel: {model}")