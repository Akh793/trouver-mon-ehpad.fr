import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const p = await b.newPage();
const errs=[]; p.on('pageerror', e=>errs.push(e.message));
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil: 'domcontentloaded' });
await p.waitForTimeout(2500);
console.log(await p.evaluate(()=>document.getElementById('couverture')?.innerText || 'BLOC ABSENT'));
console.log('ERREURS', errs.length, errs.slice(0,3));
await b.close();
