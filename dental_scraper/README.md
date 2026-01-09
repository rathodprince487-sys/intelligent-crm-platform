# Dental Clinics Scraper (Gotri, Vadodara)

## Overview
This Scrapy project scrapes dental clinics from Google Maps and visits their websites to enrich contact information (emails/phones).

## Setup
Dependencies are already installed in this environment. If you need to reinstall elsewhere:
```bash
pip install scrapy scrapy-playwright
playwright install
```

## Usage
To run the scraper and save results to `clinics.csv`:
```bash
python3 -m scrapy crawl dental_spider -O clinics.csv
```

## Structure
- `dental_scraper/spiders/dental_spider.py`: The main crawler logic.
    1. Searches Google Maps for "Dental clinics in Gotri, Vadodara".
    2. Scrolls to load results.
    3. Extract basic info from Google Maps.
    4. Follows website URLs to extract emails.
- `dental_scraper/items.py`: Data model.
- `dental_scraper/settings.py`: Configuration (Playwright, User-Agents).

## Notes
- **Google Maps Selectors**: The CSS selectors specifically for Google Maps (`div[role='feed']`, `aria-label`) are subject to change by Google. If the spider retrieves 0 results, check the selectors in `dental_spider.py`.
- **Performance**: The scraper is set to be polite (delays). It uses a headless browser (Playwright) which is resource intensive.
