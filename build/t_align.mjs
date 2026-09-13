import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
for (const w of [1440, 1280, 1100, 900]) {
  const p = await b.newPage({ viewport:{width:w,height:1100} });
  await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
  await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove();
                         document.getElementById('plus-situation').open = true; });
  await p.waitForTimeout(900);
  console.log(w, JSON.stringify(await p.evaluate(()=>{
    const out={};
    for (const g of ['grid4','grid3']) {
      const cels=[...document.querySelectorAll('.'+g+' .fld')].filter(e=>e.offsetParent);
      const par={};
      cels.forEach(c=>{
        const ctrl=c.querySelector('input,select,.seg,.in-eur');
        if(!ctrl) return;
        const ligne=Math.round(c.getBoundingClientRect().top);
        const y=Math.round(ctrl.getBoundingClientRect().top);
        (par[ligne]=par[ligne]||[]).push(y);
      });
      out[g]=Object.values(par).map(ys=>({ecart:Math.max(...ys)-Math.min(...ys)}));
    }
    return out;
  })));
  await p.close();
}
await b.close();
