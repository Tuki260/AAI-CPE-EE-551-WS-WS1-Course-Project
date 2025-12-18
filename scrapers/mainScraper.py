from . import microcenter, newegg, shopblt
import json
from json import JSONDecodeError
from datetime import datetime

class mainScraper:
    """
    mainScraper class

    This class acts as a coordinator for multiple website-specific scrapers.

    It also updates a JSON file that stores historical price data for each tracked product.
    """

    def __init__(self, json_path):
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

    def scrape_product(self, url: str):
        """
        Scrape a single product page using the correct scraper.

        Returns:
            tuple: (price, currency, brand, model)
        """
        scraper = self.determine_scraper(url)
        if scraper is None:
            # Unsupported website: fail gracefully
            print(f"[WARN] Unsupported URL (no scraper found): {url}")
            return None, None, None, None

        try:
            # calll scrape_data from all our scrapers
            return scraper.scrape_data(url)

        except (microcenter.MicrocenterScrapeError,
                newegg.NeweggScrapeError,
                shopblt.ShopBLTScrapeError) as e:
            # Scraper-specific parsing or network errors
            print(f"[WARN] Scrape failed for {url}: {e}")
            return None, None, None, None

        except Exception as e:
            # Last-resort catch so a bad URL doesn't crash everything
            print(f"[WARN] Unexpected scrape error for {url}: {e}")
            return None, None, None, None
    
    def update_json_data(self, json_path: str = "../product_data.json"):
        """
        Update product_data.json by scraping current prices for each product source.

        - Loads the JSON file containing tracked products + sources
        - Scrapes each URL for its current price
        - Appends a new entry to the 'prices' history list with timestamp
        - Writes the updated JSON back to file

        This allows gives us a running data list for plotting later
        """
        # Load tracked products from disk
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"[ERROR] Could not find JSON file: {json_path}")
            return
        except JSONDecodeError as e:
            print(f"[ERROR] JSON file is not valid: {json_path} ({e})")
            return
        except OSError as e:
            print(f"[ERROR] Could not read JSON file: {json_path} ({e})")
            return

        with open(self.json_path) as f:
            data = json.load(f)
        
        timestamp = datetime.now().isoformat()

        # Walk through each product and each website source URL
        for product_name, product_data in data.items():
            sources = product_data.get("sources", {})
            for source_name, source_data in sources.items():
                url = source_data.get("url")
                if not url:
                    print(f"[WARN] Missing URL for {product_name} -> {source_name}")
                    continue

                price, currency, brand, model = self.scrape_product(url)

                # Only store meaningful price entries
                if price is None:
                    continue

                price_entry = {"price": price, "timestamp": timestamp}

                # Ensure the history list exists before appending
                source_data.setdefault("prices", []).append(price_entry)

        # Save updated dataset back to disk
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except OSError as e:
            print(f"[ERROR] Could not write JSON file: {json_path} ({e})")


if __name__ == "__main__":
    scraper = mainScraper()
    # url = "https://www.microcenter.com/product/688526/corsair-vengeance-rgb-32gb-(2-x-16gb)-ddr5-6000-pc5-48000-cl36-dual-channel-desktop-memory-kit-cmh32gx5m2m6000z36-black"
    # url = "https://www.newegg.com/g-skill-ripjaws-m5-neo-rgb-series-32gb-ddr5-6000-cas-latency-cl36-desktop-memory-black/p/N82E16820374642?Item=N82E16820374642"
    # url = "https://www.shopblt.com/cgi-bin/shop/shop.cgi?action=thispage&thispage=011003501501_B6QC407P.shtml&order_id=198503165"
    # scraper.scrape_product(url)
    # price, currency, brand, model = scraper.scrape_product(url)
    # print(f"Price: {price}\nCurrency: {currency}\nBrand: {brand}\nModel: {model}")
    scraper.update_json_data()