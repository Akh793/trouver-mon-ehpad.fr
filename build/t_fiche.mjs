import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const p = await b.newPage({viewport:{width:1280,height:1400}});
const errs=[]; p.on('pageerror', e => errs.push(e.message));
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil: 'domcontentloaded' });
await p.fill('#cp', '69100'); await p.fill('#revenus', '1600');
await p.waitForTimeout(3000);
await p.click('[data-fin="690025192"] [data-voir]');
await p.waitForTimeout(1200);
const t = await p.evaluate(() => {
  const f = document.querySelector('.fiche, #fiche, dialog[open], .modale');
  return f ? f.innerText.replace(/\n{2,}/g,'\n') : document.body.innerText.slice(0,200);
});
console.log(t.slice(0,3500));
console.log('--- ERREURS:', errs.length, errs.slice(0,5));
await p.screenshot({path:'shot-fiche.png', fullPage:false});
await b.close();
