BOT_NAME = "dental_scraper"

SPIDER_MODULES = ["dental_scraper.spiders"]
NEWSPIDER_MODULE = "dental_scraper.spiders"

# Obey robots.txt rules (Google Maps ignores this usually, but good practice for target sites)
ROBOTSTXT_OBEY = False

# User-Agent handling
# USER_AGENT = '...' # We use rotation now
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

USER_AGENT_LIST = [] # Disabled

# SCRAPY PLAYWRIGHT SETTINGS
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

import shutil
import os
import sys

PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
    "timeout": 90 * 1000,
    "args": [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-software-rasterizer",
        "--disable-blink-features=AutomationControlled",
    ],
    "ignore_default_args": ["--enable-automation"],
}

# Auto-detect system Chromium for Streamlit Cloud (Linux)
if sys.platform.startswith("linux"):
    chrome_path = shutil.which("chromium") or shutil.which("chromium-browser") or "/usr/bin/chromium"
    if chrome_path and os.path.exists(chrome_path):
        PLAYWRIGHT_LAUNCH_OPTIONS["executable_path"] = chrome_path

# ...

DOWNLOADER_MIDDLEWARES = {
   # 'dental_scraper.middlewares.RotateUserAgentMiddleware': 400,
   # 'dental_scraper.middlewares.DentalScraperDownloaderMiddleware': 543,
}

# SUPERCHARGED: Higher concurrency
CONCURRENT_REQUESTS = 16  # Processes 16 pages simultaneously if needed

# SUPERCHARGED: Near-zero delay
DOWNLOAD_DELAY = 0.1  # Minimal delay
RANDOMIZE_DOWNLOAD_DELAY = True

# Pipelines
ITEM_PIPELINES = {
   "dental_scraper.pipelines.DentalScraperPipeline": 300,
}

# Logging
LOG_LEVEL = 'INFO'
