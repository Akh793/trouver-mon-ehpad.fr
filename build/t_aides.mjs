import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const p = await b.newPage({ viewport:{width:1440,height:1100} });
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove();
                       document.getElementById('plus-situation').open = true; });
await p.waitForTimeout(900);
const r = await p.evaluate(()=>[...document.querySelectorAll('.fld')].filter(e=>e.offsetParent).map(f=>{
  const l=f.querySelector('label'), h=f.querySelector('.fld-h');
  return { lbl: l?l.textContent.trim():'(sans)', mots: h?(h.textContent.match(/\S+/g)||[]).length:0,
           aide: h?h.textContent.trim():'' };
}));
r.forEach(x=>console.log(String(x.mots).padStart(3), '|', x.lbl.slice(0,42).padEnd(44), '|', x.aide.slice(0,90)));
console.log('TOTAL aides :', r.reduce((a,x)=>a+x.mots,0), 'mots ·', r.filter(x=>x.mots>12).length, 'au-dessus de 12 mots');
await b.close();
