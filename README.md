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

To use our code please download all necessary files/folders. Next Add product links from Microcenter, newegg or shopBLT to the "product_data.json" file, the JSON does already come preloaded with our test links. Open the "Renda_Vincent_ScottoDiVetta_Salvatore_Project.ipynb" file and run the code. The user will be prompted to select from a list of product categories or to update the data. Users should update the dat when they first open the code, as this reruns all the scrapers to ensure the data you select in the next step is the most up to date. After updating data and selecting your category the user will then select specific products within those categories. This will display the Price, currency, brand and model. Users will then be asked if they wish to plot their data, from there the historical data will be plotted onto a visual graph for easy viewing.

Required Python Libraries:
- requests
- matplotlib
- urllib.error
- erllib.request
- socket
- gzip
- http.cookiejar
- datetime
- json


### Team Contributions

Vincent:
- Made sub scrapers
- Made main scraper class
- Added to Readme
- Made Pytest class for main scraper
- Made UI plot historical Data

Salvatore:
- Turned sub scrapers into classes
- Made main program that is used by users
- Added to Readme
- Found product pages to be scraped
- Added exception handling and comments

