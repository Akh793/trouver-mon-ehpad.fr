import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const p = await b.newPage({ viewport:{width:1440,height:1100} });
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
await p.fill('#cp','69003'); await p.fill('#revenus','1600'); await p.waitForTimeout(2500);
await p.evaluate(()=>{ document.getElementById('plus-situation').open = true; document.activeElement.blur(); });
await p.waitForTimeout(700);
await (await p.$('.grid4')).screenshot({path:'a-grid4.png'});
await (await p.$('.grid3')).screenshot({path:'a-grid3.png'});
// le suffixe €/mois reste-t-il centre dans son champ ?
console.log('centrage €/mois :', JSON.stringify(await p.evaluate(()=>
  [...document.querySelectorAll('.in-eur')].filter(e=>e.offsetParent).map(w=>{
    const i=w.querySelector('input'), s=w.querySelector('span');
    const ri=i.getBoundingClientRect(), rs=s.getBoundingClientRect();
    return Math.round((rs.top+rs.height/2)-(ri.top+ri.height/2));
  }))));
await b.close();
