import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
for (const [nom, w, dark] of [['1280',1280,false],['390',390,true]]) {
  const p = await b.newPage({ viewport:{width:w,height:900}, isMobile:w<500, colorScheme: dark?'dark':'light' });
  await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
  await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
  await p.waitForTimeout(1000);
  const hs = await p.$$('h2:has(.n)');
  for (let i=0;i<hs.length;i++){ await hs[i].scrollIntoViewIfNeeded(); await p.waitForTimeout(250);
    await hs[i].screenshot({path:`h2b-${nom}-${i}.png`}); }
  await p.close();
}
await b.close();
