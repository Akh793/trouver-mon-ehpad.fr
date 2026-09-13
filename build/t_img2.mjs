import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const p = await b.newPage();
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil: 'domcontentloaded' });
await p.fill('#cp','69100'); await p.waitForTimeout(4000);
console.log(JSON.stringify(await p.evaluate(()=>[...document.querySelectorAll('img:not([alt])')].map(i=>i.className||i.tagName).slice(0,20))));
await b.close();
