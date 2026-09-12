import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const p = await b.newPage({ viewport:{width:1200,height:630}, deviceScaleFactor:1 });
await p.goto('file://' + process.cwd() + '/og.html', { waitUntil:'networkidle' });
await p.waitForTimeout(400);
await p.screenshot({ path:'../site/assets/og-image.png' });
await b.close(); console.log('og-image.png');
