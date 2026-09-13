import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
for (const w of [1440, 1280, 1024]) {
  const p = await b.newPage({ viewport:{width:w,height:1000} });
  await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
  await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove();
                         document.getElementById('plus-situation').open = true; });
  await p.waitForTimeout(900);
  console.log(w, JSON.stringify(await p.evaluate(()=>{
    const c=document.createElement('canvas').getContext('2d');
    return [...document.querySelectorAll('select')].filter(s=>s.offsetParent).map(s=>{
      const cs=getComputedStyle(s);
      c.font = cs.fontWeight+' '+cs.fontSize+' '+cs.fontFamily;
      const large = Math.max(...[...s.options].map(o=>c.measureText(o.text).width));
      const dispo = s.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
      return { id:s.id, tronque: large > dispo, manque: Math.round(large - dispo) };
    }).filter(x=>x.tronque);
  })));
  await p.close();
}
await b.close();
