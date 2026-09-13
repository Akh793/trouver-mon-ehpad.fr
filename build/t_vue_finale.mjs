import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
for (const [nom, vp] of [['bureau', {width:1280,height:1400}], ['mobile', {width:390,height:844}]]) {
  const p = await b.newPage({ viewport: vp, isMobile: vp.width<500, hasTouch: vp.width<500 });
  await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
  await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
  await p.waitForTimeout(1200);
  await p.screenshot({path:`f-haut-${nom}.png`});
  await p.fill('#cp','69100'); await p.fill('#revenus','1600'); await p.waitForTimeout(3200);
  await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
  await p.click('[data-fin="690025192"] [data-voir]'); await p.waitForTimeout(900);
  const f = await p.$('.fiche,#fiche,dialog[open],.modale');
  if (f) await f.screenshot({path:`f-fiche-${nom}.png`});
  await p.close();
}
await b.close();
