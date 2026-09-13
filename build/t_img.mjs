import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const p = await b.newPage();
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil: 'domcontentloaded' });
await p.waitForTimeout(2500);
console.log(JSON.stringify(await p.evaluate(()=>[...document.querySelectorAll('img:not([alt])')].map(i=>({src:(i.src||'').slice(-60), cls:i.className, parent:i.parentElement?.className}))),null,1));
await b.close();
