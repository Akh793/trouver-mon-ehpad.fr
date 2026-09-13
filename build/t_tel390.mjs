import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
const p = await b.newPage({ viewport:{width:390,height:844}, isMobile:true, hasTouch:true });
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
await p.fill('#cp','69003'); await p.fill('#revenus','1600'); await p.waitForTimeout(3200);
await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
console.log('largeurs :', JSON.stringify(await p.evaluate(()=>({
  doc:document.documentElement.scrollWidth, vue:document.documentElement.clientWidth,
  actDeborde:[...document.querySelectorAll('.res-act')].some(e=>e.scrollWidth>e.clientWidth+1)}))));
const c = await p.$('#liste .res'); await c.scrollIntoViewIfNeeded(); await p.waitForTimeout(300);
await c.screenshot({path:'carte-tel-390.png'});
await b.close();
