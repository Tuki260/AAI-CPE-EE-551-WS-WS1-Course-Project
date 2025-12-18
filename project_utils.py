import sys
import json
from datetime import datetime
from typing import Any
import matplotlib.pyplot as plt

def display_menu(options: list[str], prompt: str | None = None):
    """
    Display a numbered menu from a list of option strings and get user input.

    Returns:
        str: The selected option string, or None if the user chooses Exit.
    """
    while True:
        if prompt:
            print(prompt)
            print("-" * len(prompt))

        for i, option in enumerate(options, start=1):
            print(f"{i}) {option}")

        choice = input("\nPlease enter your choice: ").strip()

        # --- Case 1: Numeric input ---
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(options):
                selected = options[index]

                if selected.lower() != "exit":
                    print(f"\nYou selected: {selected}")
                    print("-" * len(f"You selected: {selected}"))

                return None if selected.lower() == "exit" else selected

            print("\nInvalid number. Please try again.\n")
            print("-" * len("Invalid number. Please try again."))
            continue

        # --- Case 2: Text input ---
        for option in options:
            if choice.lower() == option.lower():

                if option.lower() != "exit":
                    print(f"\nYou selected: {option}")
                    print("-" * len(f"You selected: {option}"))

                return None if option.lower() == "exit" else option

        print("\nInvalid choice. Please enter a valid number or option name.\n")


def get_all_categories(file_path: str) -> set[str]:
    """
    Extract all unique product categories from a products JSON file.

    Args:
        file_path (str): Path to the products JSON file.

    Returns:
        set[str]: Unique category names.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    categories = set()

    for product_data in data.values():
        category = product_data.get("category")
        if category:
            categories.add(category)

    return categories

def get_products_by_category(file_path: str, category: str) -> list[str]:
    """
    Return all product names that belong to a given category.

    Args:
        file_path (str): Path to the products JSON file.
        category (str): Category to filter by (case-insensitive).

    Returns:
        list[str]: List of product names in that category.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []
    category = category.lower()

    for product_name, product_data in data.items():
        if product_data.get("category", "").lower() == category:
            results.append(product_name)

    return results

def get_latest_prices_for_product(file_path: str, product_name: str) -> dict[str, dict[str, Any] | None]:
    """
    Load products JSON from file and return the latest price record for each source
    for the given product.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        products_json = json.load(f)

    if product_name not in products_json:
        raise KeyError(f"Product not found: {product_name}")

    sources = products_json[product_name].get("sources", {})
    latest_by_source: dict[str, dict[str, Any] | None] = {}

    for source_name, source_data in sources.items():
        price_list = source_data.get("prices", [])

        if not price_list:
            latest_by_source[source_name] = None
            continue

        latest_entry = max(
            price_list,
            key=lambda p: datetime.fromisoformat(p["timestamp"])
        )

        latest_by_source[source_name] = latest_entry

    return latest_by_source


def plot_price_history(file_path: str, product_name: str) -> None:
    """
    Plot price history over time for a product across all sources in the JSON file.

    Args:
        file_path (str): Path to the products JSON file.
        product_name (str): Exact product name key in the JSON (e.g., "Corsair Vengeance RGB DDR5 32GB").

    Raises:
        FileNotFoundError: If the JSON file can't be found.
        ValueError: If the JSON is invalid or product has no usable price data.
        KeyError: If the product_name is not in the JSON.
    """
    # Load JSON
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON format.") from e

    if product_name not in data:
        raise KeyError(f"Product not found: {product_name}")

    product = data[product_name]
    sources = product.get("sources", {})

    if not sources:
        raise ValueError(f"No sources found for product: {product_name}")

    plotted_any = False

    # Plot each source
    for source_name, source_data in sources.items():
        price_list = source_data.get("prices", [])
        if not price_list:
            continue

        points = []
        for entry in price_list:
            ts = entry.get("timestamp")
            price = entry.get("price")
            currency = entry.get("currency")

            if ts is None or price is None:
                continue
            if currency and currency != "USD":
                # If you ever support multiple currencies, convert here instead of skipping.
                continue

            try:
                t = datetime.fromisoformat(ts)
            except ValueError:
                continue

            points.append((t, float(price)))

        if not points:
            continue

        points.sort(key=lambda x: x[0])
        times = [t for t, _ in points]
        prices = [p for _, p in points]

        plt.plot(times, prices, marker="o", label=source_name)
        plotted_any = True

    if not plotted_any:
        raise ValueError(f"No usable price data found to plot for: {product_name}")

    plt.title(f"Price History: {product_name}")
    plt.xlabel("Time")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # menu_options = [
    #     "CPU",
    #     "GPU",
    #     "RAM",
    #     "Motherboard",
    #     "CPU Cooler",
    #     "Power Supply",
    #     "Case",
    #     "Update Data (Recommended when first open)",
    #     "Exit"
    # ]

    # while True:
    #     selection = display_menu(menu_options, "Choose a device:")

    #     if selection is None:
    #         print("Exiting program.")
    #         sys.exit()
    print(get_latest_prices_for_product("product_data_test.json", "Corsair Vengeance RGB DDR5 32GB"))
    plot_price_history("product_data_test.json", "Corsair Vengeance RGB DDR5 32GB")
