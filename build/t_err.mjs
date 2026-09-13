import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const p = await b.newPage({ viewport:{width:1280,height:900} });
const errs=[]; p.on('pageerror', e=>errs.push(e.message)); p.on('console', m=>{ if(m.type()==='error' && !/geopf|tile/i.test(m.text())) errs.push('console: '+m.text()); });
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
await p.fill('#cp','69003'); await p.fill('#revenus','1600'); await p.waitForTimeout(3200);
await p.click('#liste .res [data-voir]'); await p.waitForTimeout(700);
for (const o of ['prix','etab','qual','ess']) { await p.click(`[data-onglet="${o}"]`); await p.waitForTimeout(350); }
await p.evaluate(()=>{ const d=document.querySelector('.route-plus'); if(d) d.open=true; });
await p.waitForTimeout(400);
console.log('couverture remplie :', await p.evaluate(()=>{
  const c=document.getElementById('couverture'), n=document.getElementById('non-simule');
  return { couverture:c?c.children.length:0, nonSimule:n?n.children.length:0,
    etapesVisibles: document.querySelectorAll('#route > .step').length,
    etapesRepliees: document.querySelectorAll('.route-plus .step').length };
}) && JSON.stringify(await p.evaluate(()=>({
  couverture:document.getElementById('couverture')?.children.length,
  nonSimule:document.getElementById('non-simule')?.children.length,
  etapesVisibles: document.querySelectorAll('#route > .step').length,
  etapesRepliees: document.querySelectorAll('.route-plus .step').length}))));
console.log('ERREURS', errs.length, errs.slice(0,5));
await b.close();
