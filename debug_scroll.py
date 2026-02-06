from playwright.sync_api import sync_playwright
import time
import urllib.parse

def run():
    search_query = "Dentist in Gotri, Vadodara"
    q = urllib.parse.quote(search_query)
    url = f"https://www.google.com/maps/search/{q}"

    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = browser.new_page()
        
        print(f"Navigating to: {url}")
        page.goto(url)
        
        try:
            page.wait_for_selector('div[role="feed"], div[aria-label*="Results"]', timeout=20000)
            print("Feed detected.")
        except:
            print("Feed NOT detected. Taking screenshot...")
            page.screenshot(path="debug_feed_fail.png")
            browser.close()
            return

        # Inject the exact JS logic from dental_spider.py
        js_script = """
            async () => {
                const delay = ms => new Promise(res => setTimeout(res, ms));
                const collectedLinks = new Set();
                
                const scrapeGlobal = () => {
                    const classLinks = document.querySelectorAll('a.hfpxzc');
                    classLinks.forEach(a => collectedLinks.add(a.href));
                    
                    const hrefLinks = document.querySelectorAll('a[href*="/maps/place/"]');
                    hrefLinks.forEach(a => collectedLinks.add(a.href));
                };

                const findScrollable = () => {
                    let candidates = [
                        document.querySelector('div[role="feed"]'),
                        document.querySelector('div[aria-label*="Results"]'),
                        document.querySelector('div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd[aria-label]'),
                        ...Array.from(document.querySelectorAll('div')).filter(d => d.style.overflowY === 'scroll' || d.style.overflowY === 'auto')
                    ];
                    return candidates.find(c => c && c.clientHeight > 0);
                };

                let element = findScrollable();
                if (!element) return "NO_FEED_ELEMENT";

                const MAX_LOOPS = 20; // Reduced for debug
                let previousCount = 0;
                let stuckCount = 0;
                
                for(let i=0; i<MAX_LOOPS; i++) {
                    scrapeGlobal();
                    let totalFound = collectedLinks.size;
                    
                    // console.log(`Loop ${i}: Found ${totalFound}`); 
                    
                    if (totalFound >= 600) break; 
                    
                    let el = findScrollable();
                    if (el) {
                        let cards = el.querySelectorAll('div[role="article"], a[href*="/maps/place/"]');
                        if (cards.length > 0) {
                            let lastCard = cards[cards.length - 1];
                            lastCard.scrollIntoView({behavior: "smooth", block: "center"});
                        } else {
                            el.scrollTop = el.scrollHeight;
                        }
                    }
                    
                    await delay(1500);
                    
                    // Shimmy
                    if (el) {
                        el.scrollBy(0, -200);
                        await delay(200);
                        el.scrollTop = el.scrollHeight;
                    }
                    
                    scrapeGlobal();
                    let newTotal = collectedLinks.size;
                    
                    if (newTotal === previousCount) {
                        stuckCount++;
                        // Force aggressive scroll if stuck
                        if (stuckCount >= 2) {
                             if(el) {
                                 el.scrollTop = el.scrollHeight / 2;
                                 await delay(1000);
                                 el.scrollTop = el.scrollHeight;
                             }
                        }
                    } else {
                        stuckCount = 0;
                    }
                    previousCount = newTotal;
                }
                
                scrapeGlobal();
                return Array.from(collectedLinks);
            }
        """
        
        print("Executing scroll script...")
        result = page.evaluate(js_script)
        
        if result == "NO_FEED_ELEMENT":
            print("JS Script returned NO_FEED_ELEMENT")
        else:
            print(f"Scrape complete. Found {len(result)} links.")
            # print(result[:5]) # Print first 5
            
        page.screenshot(path="debug_result.png")
        print("Screenshot saved to debug_result.png")
        browser.close()

if __name__ == "__main__":
    run()
