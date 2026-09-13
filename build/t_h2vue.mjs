import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
for (const [nom, w] of [['1280',1280],['390',390]]) {
  const p = await b.newPage({ viewport:{width:w,height:900}, isMobile:w<500 });
  await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
  await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
  await p.waitForTimeout(1000);
  const h = await p.$('#bande-situation h2'); await h.scrollIntoViewIfNeeded(); await p.waitForTimeout(300);
  await h.screenshot({path:`h2-num-${nom}.png`});
  const h2 = await p.$('#bande-explorer h2, #bande-guides h2');
  if (h2) { await h2.scrollIntoViewIfNeeded(); await p.waitForTimeout(300); await h2.screenshot({path:`h2-em-${nom}.png`}); }
  await p.close();
}
await b.close();
