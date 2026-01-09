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

PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True, # Set to False to see the browser
    "timeout": 90 * 1000,  # 90 seconds for stability
}

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
