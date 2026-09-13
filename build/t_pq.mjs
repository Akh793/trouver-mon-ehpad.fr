import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
for (const w of [1440,1280,1024,860]) {
  const p = await b.newPage({ viewport:{width:w,height:900} });
  await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
  await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
  await p.waitForTimeout(900);
  console.log(w, JSON.stringify(await p.evaluate(()=>{
    const c=document.createElement('canvas').getContext('2d');
    return [...document.querySelectorAll('.fld-pq .seg button')].map(bt=>{
      const cs=getComputedStyle(bt); c.font=cs.fontWeight+' '+cs.fontSize+' '+cs.fontFamily;
      const dispo=bt.clientWidth-parseFloat(cs.paddingLeft)-parseFloat(cs.paddingRight);
      return { t:bt.textContent, tronque: c.measureText(bt.textContent).width > dispo+1 };
    });
  })));
  await p.close();
}
await b.close();
