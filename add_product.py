"""
add_product.py

Importable module to add a new product entry to product_data.json.

Use in a notebook:
    from add_product import add_product_interactive
    add_product_interactive("product_data.json")
"""

import json
import os
from typing import Dict, Optional


def load_product_data(path: str):
    """Load JSON data from disk, or return an empty dict if the file does not exist."""
    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_product_data(path: str, data: Dict):
    """Save JSON data back to disk with pretty formatting."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def prompt_sources(min_sources: int = 2, max_sources: int = 3) -> Dict:
    """
    Prompt user for sources + URLs.

    Returns:
        dict of sources in the format:
        {
            "newegg": {"url": "...", "prices": []},
            ...
        }
    """
    sources: Dict = {}

    print(f"\nEnter product sources ({min_sources}-{max_sources}).")
    print("When finished, press ENTER for source name.\n")

    while True:
        if len(sources) >= max_sources:
            print(f"Reached max of {max_sources} sources.")
            break

        source_name = input("Source name (e.g., microcenter, newegg): ").strip().lower()

        if not source_name:
            if len(sources) >= min_sources:
                break
            print(f"⚠ You must enter at least {min_sources} sources.")
            continue

        url = input(f"URL for {source_name}: ").strip()
        if not url.startswith("http"):
            print("⚠ Invalid URL. Must start with http or https.")
            continue

        sources[source_name] = {"url": url, "prices": []}

    return sources


def add_product(
    file_path: str,
    product_name: str,
    category: str,
    model: str,
    sources: Dict,
    overwrite: bool = False,
) -> bool:
    """
    Add a product to the JSON file.

    Returns:
        True if saved, False if not saved (e.g., exists and overwrite=False).
    """
    data = load_product_data(file_path)

    if product_name in data and not overwrite:
        return False

    data[product_name] = {
        "model": model,
        "category": category,
        "sources": sources,
    }

    save_product_data(file_path, data)
    return True


def add_product_interactive(file_path: str = "product_data.json"):
    """
    Interactive flow for adding a product.
    Safe to call from a Jupyter notebook.
    """
    print("\n=== Add New Product ===\n")

    product_name = input("Product name (display name): ").strip()
    category = input("Category (CPU, GPU, RAM, etc.): ").strip()
    model = input("Model number: ").strip()

    sources = prompt_sources()

    data = load_product_data(file_path)
    if product_name in data:
        overwrite = input(f"\n⚠ '{product_name}' already exists. Overwrite? (y/n): ").strip().lower()
        if overwrite != "y":
            print("Aborted. No changes made.")
            return
        saved = add_product(file_path, product_name, category, model, sources, overwrite=True)
    else:
        saved = add_product(file_path, product_name, category, model, sources, overwrite=False)

    if saved:
        print("\n✅ Product added successfully!")
        print(f"Saved to {file_path}")
    else:
        print("\nNo changes made.")


# Allows: python add_product.py
if __name__ == "__main__":
    add_product_interactive("product_data.json")
