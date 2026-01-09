BOT_NAME = "dental_scraper"

SPIDER_MODULES = ["dental_scraper.spiders"]
NEWSPIDER_MODULE = "dental_scraper.spiders"

# Obey robots.txt rules (Google Maps ignores this usually, but good practice for target sites)
ROBOTSTXT_OBEY = False

# User-Agent handling
# USER_AGENT = '...' # We use rotation now

USER_AGENT_LIST = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
]

# SCRAPY PLAYWRIGHT SETTINGS
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

import shutil
import os
import sys

# ... (Previous imports can stay or be redundant, cleaner to just start fresh logic here for launch options)

PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
    "timeout": 90 * 1000,
    "args": [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-software-rasterizer",
    ]
}

# Auto-detect system Chromium for Streamlit Cloud (Linux)
if sys.platform.startswith("linux"):
    chrome_path = shutil.which("chromium") or shutil.which("chromium-browser") or "/usr/bin/chromium"
    if chrome_path and os.path.exists(chrome_path):
        PLAYWRIGHT_LAUNCH_OPTIONS["executable_path"] = chrome_path

DOWNLOADER_MIDDLEWARES = {
   'dental_scraper.middlewares.RotateUserAgentMiddleware': 400,
   # 'dental_scraper.middlewares.DentalScraperDownloaderMiddleware': 543,
}

# OPTIMIZED: Increased concurrency for faster scraping
CONCURRENT_REQUESTS = 12  # Up from 4 - processes 3x more pages simultaneously

# OPTIMIZED: Reduced delays for speed (still respectful)
DOWNLOAD_DELAY = 0.5  # Down from 2s - 4x faster
RANDOMIZE_DOWNLOAD_DELAY = True

# Pipelines
ITEM_PIPELINES = {
   "dental_scraper.pipelines.DentalScraperPipeline": 300,
}

# Logging
LOG_LEVEL = 'INFO'
