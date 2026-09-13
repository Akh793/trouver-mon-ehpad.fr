import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const p = await b.newPage({ viewport:{width:1280,height:900} });
const errs=[]; p.on('pageerror', e=>errs.push(e.message));
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
await p.fill('#cp','69003'); await p.fill('#revenus','1600'); await p.waitForTimeout(3200);
await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
const liste = await p.$('#liste'); await liste.scrollIntoViewIfNeeded(); await p.waitForTimeout(400);
await p.hover('#liste .res:nth-child(2)'); await p.waitForTimeout(400);
console.log('carte survolee :', JSON.stringify(await p.evaluate(()=>{
  const c=document.querySelectorAll('#liste .res')[1], cs=getComputedStyle(c);
  return { transform:cs.transform, ombre:cs.boxShadow.slice(0,34), bordure:cs.borderColor.split(' ')[0] };
})));
const box = await p.evaluate(()=>{const l=document.getElementById('liste');const r=l.getBoundingClientRect();
  return {x:Math.round(r.x),y:Math.max(0,Math.round(r.y)),width:Math.round(r.width),height:Math.min(420,Math.round(r.height))};});
await p.screenshot({path:'cartes-survol.png', clip:box});
console.log('ERREURS', errs.length);
await b.close();
