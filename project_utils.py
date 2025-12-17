import sys

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





if __name__ == "__main__":
    menu_options = [
        "CPU",
        "GPU",
        "RAM",
        "Motherboard",
        "CPU Cooler",
        "Power Supply",
        "Case",
        "Update Data (Recommended when first open)",
        "Exit"
    ]

    while True:
        selection = display_menu(menu_options, "Choose a device:")

        if selection is None:
            print("Exiting program.")
            sys.exit()