import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const p = await b.newPage({ viewport:{width:1280,height:900} });
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
await p.waitForTimeout(1200);
console.log('hauteurs au repos :', JSON.stringify(await p.evaluate(()=>
  [...document.querySelectorAll('.grid4 .fld')].map(e=>Math.round(e.getBoundingClientRect().height)))));
// code postal partage par plusieurs communes
await p.type('#cp','01500'); await p.waitForTimeout(1500);
console.log('liste communes :', JSON.stringify(await p.evaluate(()=>{
  const dd=document.getElementById('cp-dd');
  if(!dd||dd.hidden) return 'fermee';
  const r=dd.getBoundingClientRect();
  const sous=document.elementFromPoint(r.left+30, r.bottom-8);
  return { options:dd.querySelectorAll('button').length, h:Math.round(r.height),
    basDeListe: sous ? (sous.closest('#cp-dd') ? 'la liste est au-dessus' : 'MASQUEE par .'+sous.className) : 'rien' };
})));
await p.screenshot({path:'grille-dd.png', clip:{x:60,y:380,width:1160,height:420}});
await b.close();
