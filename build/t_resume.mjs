import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const p = await b.newPage({ viewport:{width:1280,height:1000} });
const errs=[]; p.on('pageerror', e=>errs.push(e.message));
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
await p.fill('#cp','69100'); await p.fill('#revenus','1600'); await p.waitForTimeout(3200);
await p.click('[data-fin="690025192"] [data-voir]'); await p.waitForTimeout(900);
console.log(JSON.stringify(await p.evaluate(()=>{
  const m=(t)=>(String(t).match(/\S+/g)||[]).length;
  const top=document.querySelector('.f-top'), prix=document.querySelector('.f-prix'),
        faits=document.querySelector('.f-faits'), disp=document.querySelector('.f-dispo-l'),
        cta=document.querySelector('.f-cta'), pan=document.querySelector('.f-panneau');
  return { resumeMots: m(prix.innerText)+m(faits.innerText)+m(disp?disp.innerText:''),
           ficheMots: m(document.querySelector('.fiche,#fiche,dialog[open],.modale').innerText),
           actions: [...cta.children].map(e=>e.textContent.trim()),
           onglet: m(pan.innerText) };
}), null, 1));
const f = await p.$('.f-top'); 
const fiche = await p.$('.fiche,#fiche,dialog[open],.modale');
await fiche.screenshot({path:'r-fiche.png'});
console.log('ERREURS', errs.length, errs.slice(0,3));
await b.close();
