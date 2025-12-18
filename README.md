# AAI-CPE-EE-551-WS-WS1-Course-Project

## PC Part Web Scraper

Vincent Renda (vrenda@stevens.edu)

Salvatore Scotto Di Vetta (sscottod@stevens.edu)


### Problem Description

The problem we are trying to solve is how difficult it is to get parts for a new PC for the best price. There are many different retailers offering the same components at different prices, which makes it challenging to identify the lowest price across all websites. The prices of computer parts change frequently, making it very hard for any one person to keep track of multiple websites manually. In order to solve this problem, we plan to create a web scrapper that will get the prices of various computer parts:

- CPU
- GPU
- RAM
- Motherboard
- CPU Cooler
- Case
- Power supply

We plan to make the representation of this data easily understandable through both numerical and graphical means so that the user can completely understand how the price of any one product has changed over time and if it is the right time to buy that product.


### Program Structure

```text
AAI-CPE-EE-551-WS-WS1-Course-Project
├── README.md
├── Renda_Vincent_ScottoDiVetta_Salvatore_Project.ipynb
├── add_product.py
├── product_data.json
├── project_utils.py
├── scrapers
│   ├── __init__.py
│   ├── mainScraper.py
│   ├── microcenter.py
│   ├── newegg.py
│   └── shopblt.py
└── test_scraper.py
```

### How To Use

To use our code please download all necessary files/folders. Open the "Renda_Vincent_ScottoDiVetta_Salvatore_Project.ipynb" file and run the code. The user will be prompted to select from a list of product categories, update the data, or add new products. Users should update the data when they first open the code, as this reruns all the scrapers to ensure the data you select in the next step is the most up to date. After updating data and selecting your category the user will then select specific products within those categories. Users will then be asked if they wish to plot their data, see price changes or see price logs. Based on user selection the code will either display a graphical representation of price vs time, a percent change of lowest price for that product regardless of website, or a log with all historical data entries for that product.

Required Python Libraries:

- sys
- os
- json
- datetime
- typing
- re
- gzip
- urllib
  * urllib.request
  * urllib.error
- http.cookiejar
- socket
- numpy
- matplotlib
  * matplotlib.pyplot


### Team Contributions

Vincent:
- Made sub scrapers
- Made main scraper class
- Added to Readme
- Made Pytest class for main scraper
- Made UI plot historical Data
- Made the Historical Data Log function

Salvatore:
- Turned sub scrapers into classes
- Made main program that is used by users
- Added to Readme
- Found product pages to be scraped
- Added exception handling and comments
- Made the price change percentage function

### How we completed each requirement:

Requirements (Part 1): your program must have all the following components:
 
- Have at least two meaningful, well-defined classes that have constructors, attributes, methods, and instance objects. These two classes must have a relationship: either inheritance or composition.
  * We have 4 total classes, one for each website-specific scraper and a main class that uses composition to use the 3 website-specific scrapers
- Define at least two meaningful, well-defined functions that help solve the problem.
  * We have many function in our project_util that we used to solve the proble
- Use at least two advanced Python libraries for data and processing, such as matplotlib, PyTorch, NumPy, or Pandas. The libraries must provide critical functionality to the program and cannot be used in a superfluous way.
  * We used matplotlib to show the user price trends and numpy to show how much the price of a product has changed since last update
- Have at least two approaches to capture Exceptions and contain at least two meaningful tests using Pytest.
  * We have exception handling throughout our scraper file
  * We have 3 tests in our pytest class file
- Perform some meaningful data I/O, such as reading from a file or from a database, etc.
  * We output price data to a json for long term storage and see historical prices
- Use at least one for loop, one while loop, and one if statement.
  * We have a while loop in out jupyter notebook that keeps running till the user decides to quit
- A docstring and a few meaningful comments for each class and each function.
  * All of our function, classes, methods have docstrings and comments
- Have a README file that guides users on how to use your program.
  * Our README is complete
 
Requirements (Part 2): your program must have at least four components from the following eight components:
 
- At least one built-in library/module.
  * We import many built-in libraries
- At least two types of mutable objects, two types of immutable objects.
  * Mutable: list and dicts
  * Immutable: str and tuples
- One generator function or generator expression.
  * We have a generator function that iterates through all the price logs of a product so that the user can see all the data points
- __name__
  * We use __name__ in almost all of our files to test them individually
