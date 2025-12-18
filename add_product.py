"""
add_product.py

Interactive utility to add a new product entry to product_data.json.

The script prompts the user for:
- Product name
- Category
- Model number
- 2-3 source links (e.g., microcenter, newegg, shopblt)

The product is appended in the expected project JSON structure.
"""

import json
import os
from typing import Dict


PRODUCT_FILE = "product_data.json"


def load_product_data(path: str) -> Dict:
    """
    Load product_data.json if it exists, otherwise return empty dict.
    """
    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_product_data(path: str, data: Dict) -> None:
    """
    Save product data back to product_data.json with pretty formatting.
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def prompt_sources() -> Dict:
    """
    Prompt user for 2-3 product sources and URLs.
    """
    sources = {}

    print("\nEnter product sources (minimum 2).")
    print("When finished, press ENTER for source name.\n")

    while True:
        source_name = input("Source name (e.g., microcenter, newegg): ").strip().lower()
        if not source_name:
            if len(sources) >= 2:
                break
            print("⚠ You must enter at least 2 sources.")
            continue

        url = input(f"URL for {source_name}: ").strip()
        if not url.startswith("http"):
            print("Invalid URL. Must start with http or https.")
            continue

        sources[source_name] = {
            "url": url,
            "prices": []
        }

    return sources


def main():
    print("\n=== Add New Product ===\n")

    product_name = input("Product name (display name): ").strip()
    category = input("Category (CPU, GPU, RAM, etc.): ").strip()
    model = input("Model number: ").strip()

    sources = prompt_sources()

    product_entry = {
        "model": model,
        "category": category,
        "sources": sources
    }

    data = load_product_data(PRODUCT_FILE)

    if product_name in data:
        overwrite = input(
            f"\n⚠ '{product_name}' already exists. Overwrite? (y/n): "
        ).strip().lower()
        if overwrite != "y":
            print("Aborted. No changes made.")
            return

    data[product_name] = product_entry
    save_product_data(PRODUCT_FILE, data)

    print("\nProduct added successfully!")
    print(f"Saved to {PRODUCT_FILE}")


if __name__ == "__main__":
    main()
