import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const p = await b.newPage({ viewport:{width:1280,height:900} });
for (const u of ['/prix-ehpad/','/ehpad/abbeville/','/retours/']) {
  await p.goto('http://127.0.0.1:8899'+u, { waitUntil:'domcontentloaded' });
  await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
  await p.evaluate(()=>window.scrollTo(0,600)); await p.waitForTimeout(700);
  console.log(u.padEnd(22), JSON.stringify(await p.evaluate(()=>{
    const a=document.querySelector('.tb-avis');
    if (!a) return 'bouton absent';
    const cs=getComputedStyle(a), r=a.getBoundingClientRect();
    return { visible: cs.display!=='none' && r.width>0, fond: cs.backgroundColor,
      texte: a.textContent.trim() };
  })));
}
const tb = await p.$('#topbar'); await tb.screenshot({path:'b-seo.png'});
await b.close();
