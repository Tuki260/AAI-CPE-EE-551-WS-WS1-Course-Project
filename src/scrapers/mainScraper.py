from . import microcenter, newegg, shopblt
import json
from datetime import datetime

class mainScraper:
    """
    mainScraper class

    This class acts as a coordinator for multiple website-specific scrapers.

    It also updates a JSON file that stores historical price data for each tracked product.
    """

    def __init__(self):
        """
        Initialize the mainScraper and create a dictionary of supported scrapers.

        The dictionary keys are domains, and the values are scraper instances.
        This makes it easy to add more websites later by adding new entries if needed.

        Uses composition by containing instances of website-specific scrapers.
        """

        self.scrapers = {
            "microcenter.com": microcenter.MicrocenterScraper(),
            "newegg.com": newegg.NeweggScraper(),
            "shopblt.com": shopblt.ShopBLTScraper(),
        }

    def determine_website(self, url: str):
        """
        Determine the website based on the given URL.

        url (str): Product URL entered.

        Returns:
            str: A supported domain string if recognized, otherwise None.
        """

        if "microcenter.com" in url:
            return "microcenter.com"
        elif "newegg.com" in url:
            return "newegg.com"
        elif "shopblt.com" in url:
            return "shopblt.com"
        else:
            return None

    def determine_scraper(self, url):
        """
        Return the scraper instance that matches the URL's website.

        url (str): Product URL.

        Returns:
            object: The scraper instance if supported, otherwise None.
        """

        domain = self.determine_website(url)

        if domain in self.scrapers:
            return self.scrapers[domain]

    def scrape_product(self, url):
        """
        Scrape a single product page using the correct scraper.

        url (str): Product URL.

        Returns:
            tuple: (price, currency, brand, model)

        Website-specific scraper may raise its own custom exception if the price cannot be extracted.
        """
        scraper = self.determine_scraper(url)

        if hasattr(scraper, "scrape_data"):
            price, currency, brand, model = scraper.scrape_data(url)

        return price, currency, brand, model
    
    def update_json_data(self):
        """
        Update product_data.json by scraping current prices for each product source.

        Loads the JSON file containing tracked products + sources
        Scrapes each URL for its current price
        Appends a new entry to the 'prices' history list with timestamp
        Writes the updated JSON back to file

        This creates a growing dataset that can later be plotted/analyzed.
        """

        with open("../product_data.json") as f:
            data = json.load(f)
        
        timestamp = datetime.now().isoformat()
        for product_name, product_data in data.items():
            for source_name, source_data in product_data["sources"].items():
                url = source_data["url"]
                price, currency, brand, model = self.scrape_product(url)
                price_entry = {
                    "price": price,
                    "timestamp": timestamp
                }
                source_data["prices"].append(price_entry)
        with open("../product_data.json", "w") as f:
            json.dump(data, f, indent=4)


if __name__ == "__main__":
    scraper = mainScraper()
    # url = "https://www.microcenter.com/product/688526/corsair-vengeance-rgb-32gb-(2-x-16gb)-ddr5-6000-pc5-48000-cl36-dual-channel-desktop-memory-kit-cmh32gx5m2m6000z36-black"
    # url = "https://www.newegg.com/g-skill-ripjaws-m5-neo-rgb-series-32gb-ddr5-6000-cas-latency-cl36-desktop-memory-black/p/N82E16820374642?Item=N82E16820374642"
    # url = "https://www.shopblt.com/cgi-bin/shop/shop.cgi?action=thispage&thispage=011003501501_B6QC407P.shtml&order_id=198503165"
    # scraper.scrape_product(url)
    # price, currency, brand, model = scraper.scrape_product(url)
    # print(f"Price: {price}\nCurrency: {currency}\nBrand: {brand}\nModel: {model}")
    scraper.update_json_data()