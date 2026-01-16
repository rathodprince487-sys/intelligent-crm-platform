
import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="en-US"
        )
        page = await context.new_page()
        
        url = "https://www.google.com/maps/search/Dentist+in+Vadodara?hl=en"
        print(f"Navigating to {url}...")
        await page.goto(url)
        await page.wait_for_load_state("domcontentloaded")
        
        try:
            await page.wait_for_selector('div[role="feed"], div[aria-label*="Results"]', state="attached", timeout=10000)
            print("Feed detected via selector.")
        except:
            print("Feed selector timed out.")

        await page.screenshot(path="debug_manual_check.png")
        
        # JS logic from spider
        links = await page.evaluate("""
            () => {
                const collectedLinks = new Set();
                
                const scrapeGlobal = () => {
                    const classLinks = document.querySelectorAll('a.hfpxzc');
                    classLinks.forEach(a => collectedLinks.add(a.href));
                    
                    const hrefLinks = document.querySelectorAll('a[href*="/maps/place/"]');
                    hrefLinks.forEach(a => collectedLinks.add(a.href));
                };

                let element = document.querySelector('div[role="feed"]');
                if (!element) {
                    const candidates = document.querySelectorAll('div[aria-label]');
                    for (const c of candidates) {
                         const label = (c.getAttribute('aria-label') || "").toLowerCase();
                         if (label.includes('results') || label.includes('wyniki')) element = c;
                    }
                }
                
                if (!element) {
                    console.log("No feed element, scraping body...");
                    scrapeGlobal();
                    return Array.from(collectedLinks);
                }
                
                scrapeGlobal();
                return Array.from(collectedLinks);
            }
        """)
        
        print(f"Found {len(links)} links.")
        for l in links:
            print(f" - {l}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
