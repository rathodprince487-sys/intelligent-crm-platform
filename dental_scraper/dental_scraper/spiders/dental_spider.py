import scrapy
from scrapy_playwright.page import PageMethod
from dental_scraper.items import DentalScraperItem
import re

class DentalSpider(scrapy.Spider):
    name = "dental_spider"
    allowed_domains = ["google.com", "google.co.in"] 

    def __init__(self, search_query="Dental clinics in Gotri, Vadodara", *args, **kwargs):
        super(DentalSpider, self).__init__(*args, **kwargs)
        self.search_query = search_query
        self.seen_urls = set()

    def start_requests(self):
        base_query = self.search_query
        
        # 1. Identify Location and Base Business Type
        location = ""
        business_type = base_query
        
        if " in " in base_query:
            parts = base_query.split(" in ")
            business_type = parts[0].strip()
            location = parts[-1].strip()
        
        # 2. UNIVERSAL BUSINESS TYPE EXPANSION (Works for ANY business type!)
        # Automatically generate variations based on common patterns
        business_variants = [business_type]
        
        # Add ONLY the most effective suffixes/prefixes for speed
        business_lower = business_type.lower()
        words = business_type.split()
        
        # Priority 1: Services (highest yield)
        if 'service' not in business_lower:
            business_variants.append(f"{business_type} services")
        
        # Priority 2: Firms/Companies (professional services)
        if 'firm' not in business_lower and 'compan' not in business_lower:
            business_variants.append(f"{business_type} firm")
        
        # Priority 3: Office/Center (location-based)
        if 'office' not in business_lower and 'center' not in business_lower:
            business_variants.append(f"{business_type} office")
        
        # Priority 4: Consultant (for professional services)
        if 'consultant' not in business_lower and len(words) <= 2:
            business_variants.append(f"{business_type} consultant")
        
        # Limit to top 6 most effective variants for speed
        business_variants = list(set(business_variants))[:6]
        
        # 3. ENHANCED KEYWORD EXPANSION FOR MAXIMUM COVERAGE
        queries_to_run = []
        
        if location:
            self.logger.info(f"📍 Detected Location: {location}. Expanding search for MAXIMUM results...")
            self.logger.info(f"🔍 Business variants ({len(business_variants)}): {business_variants}")
            
            # ITERATE THROUGH ALL BUSINESS VARIANTS (Optimized)
            for biz_type in business_variants:
                # Core queries only (most effective)
                queries_to_run.append(f"{biz_type} in {location}")
                queries_to_run.append(f"{biz_type} {location}")
                
                # Quality variations ONLY for main business type
                if biz_type == business_type:
                    queries_to_run.extend([
                        f"Best {biz_type} in {location}",
                        f"Top {biz_type} in {location}",
                    ])
            
            # Minimal additional variations (high-yield only)
            queries_to_run.extend([
                f"All {business_type} in {location}",
            ])
            
            # GEOGRAPHIC SUBDIVISION STRATEGY
            # If location contains comma (e.g., "Gotri, Vadodara"), search both the specific area and broader area
            if ',' in location:
                parts = [p.strip() for p in location.split(',')]
                specific_area = parts[0]
                broader_area = parts[-1]
                
                # Search in broader area too
                queries_to_run.extend([
                    f"{business_type} in {broader_area}",
                    f"{business_type} near {broader_area}",
                    f"Best {business_type} in {broader_area}",
                    f"{business_type} {broader_area}",
                ])
                
                # Search with just specific neighborhood
                queries_to_run.extend([
                    f"{business_type} {specific_area}",
                    f"{business_type} near {specific_area}",
                ])
        else:
            queries_to_run.append(base_query)

        # Unique queries only
        queries_to_run = list(set(queries_to_run))
        
        self.logger.info(f"🚀 Running {len(queries_to_run)} search variations for comprehensive coverage!")

        for idx, q in enumerate(queries_to_run):
            # Write progress to file for UI tracking
            try:
                with open("scraper_progress.txt", "w") as f:
                    f.write(f"{idx+1}/{len(queries_to_run)}|{q}")
            except:
                pass
            
            formatted_q = q.replace(" ", "+")
            url = f"https://www.google.com/maps/search/{formatted_q}/"
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "domcontentloaded"),
                        PageMethod("wait_for_timeout", 3000), 
                    ],
                },
                callback=self.parse_search_results
            )

    async def parse_search_results(self, response):
        page = response.meta["playwright_page"]
        
        self.logger.info("Starting optimized scroll...")

        # ENHANCED SCROLLING LOGIC FOR MAXIMUM RESULTS
        place_links = await page.evaluate("""
            async () => {
                const delay = ms => new Promise(res => setTimeout(res, ms));
                const collectedLinks = new Set();
                
                const scrapeVisible = () => {
                    const links = document.querySelectorAll('a');
                    links.forEach(a => {
                        if (a.href && a.href.includes('/maps/place/')) {
                            collectedLinks.add(a.href);
                        }
                    });
                };

                let element = document.querySelector('div[role="feed"]');
                if (!element) {
                     const divs = document.querySelectorAll('div[aria-label]');
                     for (const d of divs) {
                         if (d.getAttribute('aria-label') && d.getAttribute('aria-label').includes('Results for')) {
                             element = d;
                             break;
                         }
                     }
                }
                if (!element) return Array.from(collectedLinks);

                let previousHeight = 0;
                let sameHeightCount = 0;
                
                scrapeVisible();

                // SPEED-OPTIMIZED Dynamic Scroll Loop
                // Reduced iterations but smarter detection for same coverage
                
                for(let i=0; i<400; i++) { 
                    element.scrollTop = element.scrollHeight;
                    
                    // Faster initial check
                    await delay(300); 
                    
                    let currentHeight = element.scrollHeight;
                    
                    if (currentHeight === previousHeight) {
                         // Quick secondary check
                         await delay(800);
                         scrapeVisible();
                         currentHeight = element.scrollHeight;
                         
                         if(currentHeight === previousHeight) {
                             sameHeightCount++;
                             
                             // Efficient wiggle to trigger lazy loading
                             if(sameHeightCount > 1) {
                                 element.scrollTop = element.scrollHeight - 1500;
                                 await delay(400);
                                 element.scrollTop = element.scrollHeight;
                                 await delay(600);
                                 scrapeVisible();
                             }
                             
                             // Exit after 5 stuck attempts (faster bailout)
                             if(sameHeightCount >= 5) {
                                 console.log(`Reached end after ${i} iterations with ${collectedLinks.size} results`);
                                 break;
                             }
                         } else {
                             sameHeightCount = 0;
                         }
                    } else {
                        sameHeightCount = 0;
                        scrapeVisible();
                    }
                    previousHeight = currentHeight;
                }
                
                // Final comprehensive scrape to catch any missed links
                scrapeVisible();
                
                return Array.from(collectedLinks);
            }
        """)
        
        self.logger.info(f"Scrolling complete. Found {len(place_links)} unique places.")
        
        for link in place_links:
            clean_link = link.split('?')[0]
            if clean_link in self.seen_urls:
                continue
            self.seen_urls.add(clean_link)

            yield scrapy.Request(
                clean_link,
                meta={
                    "playwright": True,
                    "playwright_include_page": False,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "h1", timeout=6000),  # Reduced from 8s
                        PageMethod("wait_for_load_state", "domcontentloaded"),
                        PageMethod("wait_for_timeout", 1200),  # Reduced from 2s
                    ],
                },
                callback=self.parse_place_detail
            )
            
        await page.close()

    def parse_place_detail(self, response):
        item = DentalScraperItem()
        item['place_url'] = response.url
        
        item['clinic_name'] = response.css('h1::text').get()
        if not item['clinic_name']:
             self.logger.warning(f"No name found for {response.url}")
        
        item['address'] = response.css('button[data-item-id="address"]::attr(aria-label)').get()
        if item['address']:
            item['address'] = item['address'].replace("Address: ", "").strip()
        else:
            item['address'] = response.css('button[data-item-id="address"] .fontBodyMedium::text').get()

        item['phone_number'] = response.css('button[data-item-id^="phone"]::attr(aria-label)').get()
        if item['phone_number']:
            item['phone_number'] = item['phone_number'].replace("Phone: ", "").strip()
        else:
             item['phone_number'] = response.css('button[data-item-id^="phone"] .fontBodyMedium::text').get()

        # ENHANCED WEBSITE EXTRACTION with multiple fallback selectors
        website_selectors = [
            'a[data-item-id="authority"]::attr(href)',
            'a[data-item-id^="authority"]::attr(href)',
            'a[aria-label*="Website"]::attr(href)',
            'a[href*="http"][data-item-id*="authority"]::attr(href)',
        ]
        
        item['website_url'] = None
        for selector in website_selectors:
            item['website_url'] = response.css(selector).get()
            if item['website_url']:
                self.logger.info(f"✅ Website found using CSS: {selector}")
                break
        
        # XPath fallbacks if CSS selectors fail
        if not item['website_url']:
            xpath_selectors = [
                '//a[contains(@aria-label, "Website:")]/@href',
                '//a[contains(@data-item-id, "authority")]/@href',
                '//a[contains(@href, "http") and contains(@aria-label, "ebsite")]/@href',
            ]
            for xpath in xpath_selectors:
                item['website_url'] = response.xpath(xpath).get()
                if item['website_url']:
                    self.logger.info(f"✅ Website found using XPath: {xpath}")
                    break
        
        if not item['website_url']:
            self.logger.warning(f"⚠️ No website found for {item['clinic_name']} - {response.url}")

        if item['website_url']:
            # Clean up the URL if it's a Google redirect
            if 'google.com/url?q=' in item['website_url']:
                import urllib.parse
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(item['website_url']).query)
                if 'q' in parsed:
                    item['website_url'] = parsed['q'][0]
            
            self.logger.info(f"🌐 Visiting website: {item['website_url']}")
            yield scrapy.Request(
                item['website_url'],
                callback=self.parse_website,
                meta={'item': item}, 
                errback=self.errback_website,
                dont_filter=True
            )
        else:
            # No website found, yield item without email
            item['email'] = None
            yield item

    def parse_website(self, response):
        item = response.meta['item']
        html_text = response.text
        
        # Extract emails with improved regex
        emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html_text))
        # Filter out common false positives
        emails = {e for e in emails if not any(x in e.lower() for x in ['example.com', 'sentry', 'schema.org', 'w3.org'])}
        
        phones = set(re.findall(r'(?:\+91[\-\s]?)?[6789]\d{9}|0265[\-\s]?\d{6,8}', html_text))
        
        item['email'] = ", ".join(emails) if emails else None
        
        if item['email']:
            self.logger.info(f"📧 Email(s) found: {item['email']}")
        else:
            self.logger.warning(f"⚠️ No email found on website: {response.url}")
        
        if not item.get('phone_number') and phones:
             item['phone_number'] = ", ".join(phones)
             
        yield item

    def errback_website(self, failure):
        item = failure.request.meta['item']
        item['email'] = None
        self.logger.error(f"❌ Failed to visit website {failure.request.url}: {failure.value}")
        yield item
