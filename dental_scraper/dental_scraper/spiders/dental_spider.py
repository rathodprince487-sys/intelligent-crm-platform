import scrapy
from scrapy_playwright.page import PageMethod
from dental_scraper.items import DentalScraperItem
import re
import urllib.parse
import os

class DentalSpider(scrapy.Spider):
    name = "dental_spider"
    allowed_domains = ["google.com", "google.co.in", "google.pl"]

    def __init__(self, search_query="Dental clinics in Gotri, Vadodara", *args, **kwargs):
        super(DentalSpider, self).__init__(*args, **kwargs)
        self.search_query = search_query
        self.total_places = 0
        self.processed_places = 0
        self.progress_file = "../scraper_progress.txt"
        self.seen_urls = set()
        self.update_progress("Starting...")

    def update_progress(self, status=None):
        try:
            display = status if status else f"{self.processed_places}/{self.total_places}"
            with open(self.progress_file, "w") as f:
                f.write(f"{display}|{self.search_query}")
        except Exception:
            pass

    def start_requests(self):
        # STRATEGY: Start at Google Home to handle global consent cookie first.
        # This bypasses the stricter checks on Google Maps search URLs.
        url = "https://www.google.com/?hl=en"
        yield scrapy.Request(
            url,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_context": "persistent_session", # VITAL: Share context/cookies
                "playwright_context_kwargs": {
                    "viewport": {"width": 1920, "height": 1080},
                    "locale": "en-US", # Try to force English locale at browser level
                },
                "playwright_page_methods": [
                    PageMethod("wait_for_load_state", "domcontentloaded"),
                    PageMethod("wait_for_timeout", 2000),
                ],
            },
            callback=self.parse_google_home
        )

    async def parse_google_home(self, response):
        page = response.meta["playwright_page"]
        
        # 1. HANDLE CONSENT ON GOOGLE HOME
        self.logger.info("🏠 Landed on Google Home. Checking for consent...")
        self.update_progress("Checking Consent...")
        
        try:
            # Check for consent buttons
            buttons = page.locator('button')
            count = await buttons.count()
            consent_clicked = False
            
            # Keywords to LOOK FOR (Prioritize Acceptance/Rejection)
            consent_keywords = [
                'accept', 'agree', 'allow', 'consent',
                'zgadzam', 'akceptuj', 'zaakceptuj', # Polish
                'odrzuć', 'reject', # Reject
                'zustimmen', 'akzeptieren', # German
                'j\'accepte', 'accepter', # French
                'aceptar', # Spanish
                'accetta', # Italian
                'alle akzeptieren', 'accept all',
                'alles accepteren',
                'hyväksy',
            ]
            avoid_keywords = ['more options', 'więcej opcji', 'customize', 'personalize', 'manage options']

            for i in range(count):
                btn = buttons.nth(i)
                if await btn.is_visible():
                    text = (await btn.inner_text()).lower()
                    aria = (await btn.get_attribute('aria-label') or "").lower()
                    combined_text = f"{text} {aria}"
                    
                    if any(bad in combined_text for bad in avoid_keywords):
                        continue
                        
                    if any(good in combined_text for good in consent_keywords):
                        self.logger.info(f"🍪 Found Consent Button on Home: '{text}' (Aria: {aria}). Clicking...")
                        await btn.click()
                        await page.wait_for_load_state("networkidle")
                        await page.wait_for_timeout(3000)
                        consent_clicked = True
                        break
            
            if not consent_clicked:
                self.logger.info("✅ No obvious consent button found on Home. Assuming clean session/already consented.")
            else:
                self.logger.info("✅ Consent handled on Home.")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Error handling home consent: {e}")

        # 2. GENERATE SEARCH QUERIES
        base_query = self.search_query
        location = ""
        business_type = base_query
        
        if " in " in base_query:
            parts = base_query.split(" in ")
            business_type = parts[0].strip()
            location = parts[-1].strip()
        
        business_variants = [business_type]
        business_lower = business_type.lower()
        words = business_type.split()
        
        if 'service' not in business_lower:
            business_variants.append(f"{business_type} services")
        if 'firm' not in business_lower and 'compan' not in business_lower:
            business_variants.append(f"{business_type} firm")
        if 'office' not in business_lower and 'center' not in business_lower:
            business_variants.append(f"{business_type} office")
        if 'consultant' not in business_lower and len(words) <= 2:
            business_variants.append(f"{business_type} consultant")
            
        business_variants = list(set(business_variants))
        
        queries_to_run = []
        if location:
            self.logger.info(f"📍 Detected Location: {location}. Expanding search...")
            self.update_progress("Preparing Search...")
            for biz_type in business_variants:
                queries_to_run.append(f"{biz_type} in {location}")
            queries_to_run.append(f"{business_type} {location}")
        else:
            queries_to_run.append(base_query)
            
        queries_to_run = list(set(queries_to_run))
        self.logger.info(f"🚀 Generated {len(queries_to_run)} search variations.")

        # 3. START MAPS SCRAPING (Using SAME Context/Page)
        # We drive the page manually here to ensure session continuity
        
        for idx, q in enumerate(queries_to_run):
            # Using + for spaces
            encoded_q = q.replace(" ", "+")
            # Force English result interface
            search_url = f"https://www.google.com/maps/search/{encoded_q}?hl=en"
            
            self.logger.info(f"📍 Manually navigating to: {search_url}")
            self.update_progress("Navigating to Maps...")
            
            try:
                await page.goto(search_url, timeout=30000)
                await page.wait_for_load_state("domcontentloaded")
                
                # Copy of the waiting logic from previous `parse_search_results` params
                try:
                    await page.wait_for_selector("div[role='feed'], h1", timeout=15000, state="attached")
                except:
                    pass
                
                # Now invoke the scraping logic directly
                # We iterate over the async generator
                async for req in self.scrape_maps_results(page, search_url):
                    yield req
                    
            except Exception as e:
                self.logger.error(f"Failed to navigate/scrape {search_url}: {e}")
                
        # Close page only after all searches are done
        await page.close()

    async def scrape_maps_results(self, page, url):
        self.update_progress("Arrived at Maps...")
        self.logger.info(f"📍 Parsing Maps URL: {url}")
        
        # Take a snapshot of what we see immediately
        # await page.screenshot(path="../debug_arrival.png")
        
        # Double check consent just in case (Maps sometimes has its own)
        try:
            if "consent" in page.url:
                self.logger.warning("⚠️ Still hitting consent on Maps! Attempting secondary click...")
                buttons = page.locator('button')
                count = await buttons.count()
                for i in range(count):
                    btn = buttons.nth(i)
                    if await btn.is_visible():
                        text = (await btn.inner_text()).lower()
                        if 'reject' in text or 'odrzuć' in text or 'accept' in text or 'zgadzam' in text:
                             await btn.click(force=True)
                             await page.wait_for_load_state("networkidle")
                             break
        except:
            pass

        self.logger.info("⏳ Waiting for results feed...")
        try:
            # Wait for generic result container
            await page.wait_for_selector('div[role="feed"], div[aria-label*="Results"]', state="attached", timeout=10000)
            self.logger.info("✅ Results feed detected!")
            self.update_progress("Feed Detected...")
        except:
             self.logger.warning("⚠️ Feed selector timeout. Trying JS fallback...")
             self.update_progress("Retrying Feed...")

        place_links = await page.evaluate("""
            async () => {
                const delay = ms => new Promise(res => setTimeout(res, ms));
                const collectedLinks = new Set();
                
                // Verified Selector from Browser Audit
                const scrapeGlobal = () => {
                    // Primary: Verified Class from Google
                    const classLinks = document.querySelectorAll('a.hfpxzc');
                    classLinks.forEach(a => collectedLinks.add(a.href));
                    
                    // Secondary: Fallback to href pattern
                    const hrefLinks = document.querySelectorAll('a[href*="/maps/place/"]');
                    hrefLinks.forEach(a => collectedLinks.add(a.href));
                };

                // Verified Container: role="feed"
                let element = document.querySelector('div[role="feed"]');
                if (!element) {
                    const candidates = document.querySelectorAll('div[aria-label]');
                    for (const c of candidates) {
                         const label = (c.getAttribute('aria-label') || "").toLowerCase();
                         if (label.includes('results') || label.includes('wyniki')) element = c;
                    }
                }
                
                // If still no element, we can't scroll effectively, but we can still Scrape what is visible
                if (!element) {
                    console.log("⚠️ No specific feed element found. Scraping body...");
                    scrapeGlobal();
                    // Try to scroll the body just in case
                    window.scrollTo(0, document.body.scrollHeight);
                    await delay(1000);
                    scrapeGlobal();
                    return Array.from(collectedLinks);
                }

                console.log("✅ using element:", element);

                // Scroll Strategy
                let previousHeight = 0;
                let sameHeightCount = 0;
                
                for(let i=0; i<40; i++) { 
                    scrapeGlobal(); // Scrape everything visible
                    
                    element.scrollTop = element.scrollHeight;
                    await delay(1000); 
                    
                    let currentHeight = element.scrollHeight;
                    if (currentHeight === previousHeight) {
                         await delay(1500);
                         currentHeight = element.scrollHeight;
                         if(currentHeight === previousHeight) {
                             sameHeightCount++;
                             // Try to press End key
                             // document.dispatchEvent(new KeyboardEvent('keydown', {'key': 'End'})); 
                             
                             if(sameHeightCount >= 5) break;
                         } else { sameHeightCount = 0; }
                    } else { sameHeightCount = 0; }
                    previousHeight = currentHeight;
                }
                
                scrapeGlobal();
                return Array.from(collectedLinks);
            }
        """)
        
        self.logger.info(f"Found {len(place_links)} places.")
        
        if len(place_links) == 0:
            self.logger.warning("⚠️ No places found! Taking debug screenshot...")
            await page.screenshot(path="../debug_failure.png", full_page=True)
            self.update_progress("No leads found (Check debug_failure.png)")
        
        self.update_progress(f"Extracting {len(place_links)} leads...")
        self.total_places += len(place_links)
        self.update_progress()
        
        for link in place_links:
            clean_link = link.split('?')[0]
            if clean_link in self.seen_urls: continue
            self.seen_urls.add(clean_link)

            yield scrapy.Request(
                clean_link,
                meta={
                    "playwright": True,
                    "playwright_include_page": False,
                    "playwright_context": "persistent_session", # Keep using same context
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "h1", timeout=5000), 
                    ],
                },
                callback=self.parse_place_detail,
                errback=self.errback_detail
            ) 


    def parse_place_detail(self, response):
        self.logger.info(f"📍 Scraped Detail: {response.url}")
        item = DentalScraperItem()
        item['place_url'] = response.url
        item['clinic_name'] = response.css('h1::text').get()
        
        # Address
        addr = response.css('button[data-item-id="address"]::attr(aria-label)').get() or ""
        item['address'] = re.sub(r'^.*?:', '', addr).strip()

        # Phone
        phone = response.css('button[data-item-id^="phone"]::attr(aria-label)').get() or ""
        item['phone_number'] = re.sub(r'^.*?:', '', phone).strip()

        # Website
        website_selectors = [
            'a[data-item-id="authority"]::attr(href)',
            'a[aria-label*="Website"]::attr(href)',
        ]
        item['website_url'] = None
        for sel in website_selectors:
            val = response.css(sel).get()
            if val:
                item['website_url'] = val
                break
        
        if item['website_url']:
             # Visit website for email
             yield scrapy.Request(
                item['website_url'],
                callback=self.parse_website,
                meta={'item': item},
                errback=self.errback_website,
                dont_filter=True
             )
        else:
            item['email'] = None
            self.processed_places += 1
            self.update_progress()
            yield item

    def parse_website(self, response):
        item = response.meta['item']
        html = response.text
        emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html))
        emails = {e for e in emails if not any(x in e.lower() for x in ['example.com', 'sentry', 'w3.org', '.png', '.jpg'])}
        item['email'] = ", ".join(emails) if emails else None
        self.processed_places += 1
        self.update_progress()
        yield item

    def errback_website(self, failure):
        item = failure.request.meta['item']
        item['email'] = None
        self.processed_places += 1
        self.update_progress()
        yield item

    def errback_detail(self, failure):
        self.logger.error(f"❌ Failed to scrape detail page: {failure.request.url} - {failure.value}")
        # Yield a partial item if possible, or just mark as processed
        # Since we don't have partial data here (only URL), we just skip it.
        # But we MUST update progress.
        self.processed_places += 1
        self.update_progress()

    custom_settings = {
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": True,
            "timeout": 60000,  # 60s launch timeout
        },
        "DOWNLOAD_TIMEOUT": 30, # Reduced timeout for faster failure on bad sites
        "CONCURRENT_REQUESTS": 16, # Increased concurrency
        "CONCURRENT_REQUESTS_DOMAIN": 16,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1.0, # Reduced from 5.0
        "AUTOTHROTTLE_MAX_DELAY": 30,
        "PLAYWRIGHT_ABORT_REQUEST": lambda req: req.resource_type in ["image", "stylesheet", "font", "media"],
    }

