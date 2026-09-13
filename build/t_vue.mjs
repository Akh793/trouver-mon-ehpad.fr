import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
for (const [nom, vp] of [['1280', {width:1280,height:900}], ['390', {width:390,height:844}]]) {
  const p = await b.newPage({ viewport: vp });
  await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
  await p.fill('#cp','69003'); await p.fill('#revenus','1600'); await p.waitForTimeout(3200);
  await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
  const el = await p.$('#total-card');
  await el.scrollIntoViewIfNeeded(); await p.waitForTimeout(500);
  await el.screenshot({ path: `card-${nom}.png` });
  const r = await p.evaluate(()=>{
    const q=(s)=>{const e=document.querySelector(s); if(!e) return null; const b=e.getBoundingClientRect(); return Math.round(b.height)+'x'+Math.round(b.width);};
    return { share:q('#share-btn'), rouge:q('#action-rouge'), opt:q('.share-opt'), card:q('#total-card') };
  });
  console.log(nom, JSON.stringify(r));
  await p.close();
}
await b.close();
