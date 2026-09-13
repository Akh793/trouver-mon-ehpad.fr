import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const p = await b.newPage({ viewport:{width:1440,height:1000} });
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove();
                       document.getElementById('plus-situation').open = true; });
await p.waitForTimeout(900);
console.log(JSON.stringify(await p.evaluate(()=>{
  const v=[...document.querySelectorAll('.grid3 .fld')].filter(e=>e.offsetParent);
  const lignes={};
  v.forEach(e=>{const r=e.getBoundingClientRect(); const y=Math.round(r.top);
    (lignes[y]=lignes[y]||[]).push(Math.round(r.height));});
  return lignes;
}), null, 1));
await b.close();
