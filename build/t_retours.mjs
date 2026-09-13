import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
for (const [nom, w] of [['1280',1280],['390',390]]) {
  const p = await b.newPage({ viewport:{width:w,height:1200}, isMobile:w<500 });
  const errs=[]; p.on('pageerror', e=>errs.push(e.message));
  await p.goto('http://127.0.0.1:8899/retours/', { waitUntil:'domcontentloaded' });
  await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
  await p.waitForTimeout(1000);
  // le piege doit etre invisible et hors tabulation
  const r = await p.evaluate(()=>{
    const pg=document.querySelector('.piege'), inp=document.getElementById('r-site');
    const de=document.documentElement;
    return { piegeVisible: pg.getBoundingClientRect().right > 0,
      piegeTab: inp.tabIndex, liste: document.getElementById('r-liste').textContent.trim().slice(0,50),
      debordement: de.scrollWidth > de.clientWidth,
      compteur: document.getElementById('r-reste').textContent };
  });
  // envoi trop court
  await p.fill('#r-message','court');
  await p.click('#r-envoi'); await p.waitForTimeout(300);
  const e1 = await p.evaluate(()=>document.getElementById('r-etat').textContent);
  // envoi normal, API absente
  await p.fill('#r-message','Le calculateur m’a beaucoup aidé pour comparer trois établissements.');
  await p.click('#r-envoi'); await p.waitForTimeout(500);
  const e2 = await p.evaluate(()=>document.getElementById('r-etat').textContent);
  const c = await p.evaluate(()=>document.getElementById('r-reste').textContent);
  console.log(nom, JSON.stringify({...r, msgCourt:e1, msgEnvoi:e2, compteurApres:c, errs:errs.length}));
  if (w===1280) await p.screenshot({path:'retours.png', clip:{x:0,y:0,width:1280,height:1200}});
  await p.close();
}
await b.close();
