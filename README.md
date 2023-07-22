
# NOTAM Scraper for Slovenia

This Python script scrapes the NOTAM (Notice to Airmen) data from the website of [Slovenia Control](https://www.sloveniacontrol.si/Strani/Summary-C.aspx) and extracts relevant information like NOTAM number, Q-codes, altitudes, timestamps, and KML links. It converts altitude values from feet to meters and organizes the data based on the start and end dates of the NOTAMs. Scripts ending with _G will hiding NOTAMS which are not important for paragliding and hangliding pilots.

## Features

- Scrapes NOTAM data from the Slovenia Control website.
- Converts altitude values in F) and G) sections from feet to meters but showing both values
- Filters NOTAMs for the current day and presents the data in a structured format.
- Provides KML links for each NOTAM, allowing visualization on a map.

## How it works

The script uses the following Python libraries:

- `requests` for making HTTP GET requests to fetch the website's HTML content.
- `BeautifulSoup` for parsing the HTML content and extracting NOTAM data elements.
- `datetime` and `pytz` for handling dates and time zones.
- `re` (regular expression) for pattern matching to extract date strings.

## Usage

1. Install the required libraries using `pip`:

```bash
pip install requests beautifulsoup4
```

2. Run one of the scripts


The script will print the NOTAM data for the current day or (3 days), or (1 week) or (1 month), including converted altitudes and KML links for visualization.

## License

This project is licensed under the [MIT License](LICENSE).

## Disclaimer

Please note that the data displayed by this scraper is obtained from the Slovenia Control website and may be subject to change or inaccuracies. The developers are not responsible for any issues arising from the use of the data.