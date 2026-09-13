import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const p = await b.newPage({ viewport:{width:1440,height:1000} });
const errs=[]; p.on('pageerror', e=>errs.push(e.message));
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
await p.fill('#cp','69003'); await p.fill('#revenus','1600'); await p.waitForTimeout(2500);
await p.evaluate(()=>{ document.getElementById('plus-situation').open = true; document.activeElement.blur(); });
await p.waitForTimeout(600);
// le libelle le plus long du select est-il encore tronque ?
console.log('select enfants :', JSON.stringify(await p.evaluate(()=>{
  const s=document.getElementById('enfants'), cs=getComputedStyle(s);
  const c=document.createElement('canvas').getContext('2d');
  c.font = cs.fontWeight+' '+cs.fontSize+' '+cs.fontFamily;
  const txt=s.options[0].text;
  const dispo = s.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
  return { police:cs.fontSize, texte:Math.round(c.measureText(txt).width), place:Math.round(dispo),
           tronque: c.measureText(txt).width > dispo };
})));
const g = await p.$('.grid3'); await g.scrollIntoViewIfNeeded(); await p.waitForTimeout(400);
await p.hover('.grid3 .fld:nth-child(2)'); await p.waitForTimeout(400);
await g.screenshot({path:'grid3.png'});
console.log('hauteurs ligne 1 :', JSON.stringify(await p.evaluate(()=>
  [...document.querySelectorAll('.grid3 .fld')].filter(e=>!e.hidden).slice(0,4).map(e=>Math.round(e.getBoundingClientRect().height)))));
console.log('ERREURS', errs.length, errs.slice(0,3));
await b.close();
