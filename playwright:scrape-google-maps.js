const { chromium } = require("playwright");

(async () => {
  const query = process.argv[2] || "dentist Vadodara";

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  await page.goto(
    `https://www.google.com/maps/search/${encodeURIComponent(query)}`,
    { waitUntil: "networkidle", timeout: 60000 }
  );

  await page.waitForSelector('a[href*="/maps/place"]');

  for (let i = 0; i < 10; i++) {
    await page.mouse.wheel(0, 1200);
    await page.waitForTimeout(1500);
  }

  const places = await page.$$eval(
    'a[href*="/maps/place"]',
    els => [...new Set(els.map(e => e.href.split("&")[0]))]
  );

  const results = [];

  for (const place of places.slice(0, 10)) {
    await page.goto(place, { waitUntil: "networkidle" });
    await page.waitForTimeout(2000);

    const website = await page.$eval(
      'a[data-item-id="authority"]',
      el => el.href
    ).catch(() => "");

    results.push({ placeUrl: place, website });
  }

  console.log(JSON.stringify(results));
  await browser.close();
})();
