import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
const compte = (t)=> (t.trim().match(/\S+/g)||[]).length;
const etats = [
  ['1. premiere visite',        async p=>{}],
  ['2. code postal seul',       async p=>{ await p.fill('#cp','69003'); await p.waitForTimeout(2800); }],
  ['3. situation renseignee',   async p=>{ await p.fill('#cp','69003'); await p.fill('#revenus','1600'); await p.waitForTimeout(3000); }],
];
for (const [nom, prep] of etats) {
  const p = await b.newPage({ viewport:{width:1280,height:1000} });
  await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
  await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
  await prep(p); await p.waitForTimeout(600);
  const r = await p.evaluate(()=>{
    const vis = (e)=>{ const s=getComputedStyle(e); return s.display!=='none' && s.visibility!=='hidden' && e.offsetParent!==null; };
    const zone = (sel)=>{ const e=document.querySelector(sel); return e&&vis(e) ? (e.innerText.match(/\S+/g)||[]).length : 0; };
    return {
      total: (document.body.innerText.match(/\S+/g)||[]).length,
      haut: zone('#bande-situation'),
      resultats: zone('#bande-carte'),
      sources: zone('#bande-sources'),
      faq: zone('#bande-faq'),
      route: zone('#route'),
    };
  });
  console.log(nom.padEnd(26), JSON.stringify(r));
  await p.close();
}
// fiche ouverte
const p = await b.newPage({ viewport:{width:1280,height:1000} });
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
await p.fill('#cp','69003'); await p.fill('#revenus','1600'); await p.waitForTimeout(3000);
await p.click('#liste .res [data-voir]'); await p.waitForTimeout(900);
console.log('4. fiche, onglet Essentiel', JSON.stringify(await p.evaluate(()=>{
  const f=document.querySelector('.fiche,#fiche,dialog[open],.modale');
  const t=f?f.innerText:'';
  const res=document.querySelector('.f-prix'), faits=document.querySelector('.f-faits');
  return { fiche:(t.match(/\S+/g)||[]).length,
    resume: res?((res.innerText+ (faits?faits.innerText:'')).match(/\S+/g)||[]).length : 0 };
})));
await b.close();
