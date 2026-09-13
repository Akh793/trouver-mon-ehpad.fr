import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
for (const w of [1440, 1280, 1100, 900, 700]) {
  const p = await b.newPage({ viewport:{width:w,height:1100} });
  await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
  await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove();
                         document.getElementById('plus-situation').open = true; });
  await p.waitForTimeout(900);
  console.log(w, JSON.stringify(await p.evaluate(()=>{
    const r = {};
    for (const g of ['grid4','grid3']) {
      const labs = [...document.querySelectorAll('.'+g+' .fld')].filter(e=>e.offsetParent)
        .map(e=>e.querySelector('label')).filter(Boolean);
      const lignes = labs.map(l=>{
        const lh = parseFloat(getComputedStyle(l).lineHeight);
        return Math.round(l.getBoundingClientRect().height / lh);
      });
      r[g] = { max: Math.max(...lignes), rep: lignes.join('') };
    }
    return r;
  })));
  await p.close();
}
await b.close();
