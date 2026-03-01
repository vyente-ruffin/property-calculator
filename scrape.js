const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(process.argv[2], { timeout: 30000 });
  const text = await page.locator('body').innerText();
  console.log(text);
  await browser.close();
})();
