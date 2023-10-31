# NOTAM Parser for Slovenia

This Python script parses NOTAM (Notice to Airmen) data from the [Slovenia Control](https://www.sloveniacontrol.si/Strani/Summary-C.aspx) website and extracts relevant information such as NOTAM numbers, Q-codes, altitudes, timestamps, and KML links. It converts altitude values from feet to meters and organizes the data based on the start and end dates of the NOTAMs. Scripts ending with `_G` are designed to hide NOTAMs that are not relevant to paragliding and hang gliding pilots.

## Features

- Scrapes NOTAM data from the Slovenia Control website.
- Converts altitude values in the F) and G) sections from feet to meters, displaying both units.
- Filters NOTAMs for the current day and presents the data in a structured format.
- Provides KML links for each NOTAM, allowing visualization in external apps like [Google Earth](https://www.google.com/earth/about/versions/) or via open-source tools, as demonstrated in the [NOTAMtoday Telegram group](https://t.me/NOTAMtoday).

## How it Works

The script uses the following Python libraries:

- `requests` for making HTTP GET requests to fetch the website's HTML content.
- `BeautifulSoup` for parsing HTML content and extracting NOTAM data elements.
- `datetime` and `pytz` for handling dates and time zones.
- `re` (regular expression) for pattern matching to extract date strings.

## Usage

1. Install the required libraries using `pip`:

    ```bash
    pip install requests beautifulsoup4
    ```

2. Run one of the scripts.

The script will print NOTAM data for the current day, 3 days, 1 week, or 1 month, including converted altitudes and KML links for visualization. As mentioned earlier, scripts ending with the letter `_G` are built to ignore NOTAMs that are not relevant for paragliding, hang gliding, and drone pilots.

- To store NOTAMs in JSON files, set the default value from `False` to `True`:
- To download KML files from the links in JSON files, set the default value from `False` to `True`:
- To unzip the KML files, set the default value from `False` to `True`:

```python
SAVE_JSON_FILES = False
```

## License

This project is licensed under the [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT). 
If you use the code in your project, a reference to the original code would be appreciated. Thank you.

For more details, see the [LICENSE](LICENSE) file in this repository.

## Disclaimer

Please note that the data displayed by this scraper is obtained from the Slovenia Control website and may be subject to change or inaccuracies. The developers are not responsible for any issues arising from the use of this data.

- `scrapedSiteExample.html` is an example of the website we are scraping. 
  If you encounter issues or inaccuracies while scraping, 
  it might be due to changes in the content structure of the Slovenia control website. 
  Use `scrapedSiteExample.html` for future reference to identify what may have changed.

---

Feel free to use this revised version to improve the readability and clarity of your README.