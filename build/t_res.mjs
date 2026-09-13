import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
for (const [nom, rev] of [['sans situation', null], ['avec situation', '1600']]) {
  const p = await b.newPage({ viewport:{width:1280,height:900} });
  const errs=[]; p.on('pageerror', e=>errs.push(e.message));
  await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
  await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
  await p.fill('#cp','69003'); if (rev) await p.fill('#revenus', rev);
  await p.waitForTimeout(3200);
  await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
  console.log('--- ' + nom + ' ---');
  console.log(await p.evaluate(()=>document.getElementById('total-card').innerText.split('\n').slice(0,4).join('\n')));
  console.log('carte 1 :', (await p.evaluate(()=>document.querySelector('#liste .res').innerText.replace(/\n/g,' | ').slice(0,150))));
  const el = await p.$('#total-card'); await el.scrollIntoViewIfNeeded(); await p.waitForTimeout(300);
  await el.screenshot({path:`r-total-${rev?'situ':'nu'}.png`});
  console.log('ERREURS', errs.length, errs.slice(0,2));
  await p.close();
}
await b.close();
