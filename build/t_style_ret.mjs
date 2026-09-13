import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
for (const [nom, w] of [['1280',1280],['390',390]]) {
  const p = await b.newPage({ viewport:{width:w,height:1200}, isMobile:w<500 });
  const errs=[]; p.on('pageerror', e=>errs.push(e.message));
  await p.goto('http://127.0.0.1:8899/retours/', { waitUntil:'domcontentloaded' });
  await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
  await p.waitForTimeout(900);
  console.log(nom, JSON.stringify(await p.evaluate(()=>{
    const de=document.documentElement, av=document.querySelector('.avert'), pg=document.querySelector('.page');
    const th=document.querySelector('#layout .head-act .tb-icon');
    const ra=av.getBoundingClientRect(), rp=pg.getBoundingClientRect();
    const rt=th?th.getBoundingClientRect():null;
    return {
      avertColonnes: getComputedStyle(av).gridTemplateColumns.split(' ').length,
      avertHauteur: Math.round(ra.height),
      pageCentree: Math.abs(Math.round(rp.left - (de.clientWidth - rp.right))) <= 2,
      themeDepuisDroite: rt ? Math.round(de.clientWidth - rt.right) : null,
      debordement: de.scrollWidth > de.clientWidth };
  })));
  await p.screenshot({path:`ret-${nom}.png`, clip:{x:0,y:0,width:w,height:1100}});
  if (errs.length) console.log('   ERREURS', errs);
  await p.close();
}
const p2 = await b.newPage({ viewport:{width:1280,height:800} });
for (const u of ['/notre-methodologie.html','/qui-sommes-nous.html','/mentions-legales.html','/']) {
  await p2.goto('http://127.0.0.1:8899'+u, { waitUntil:'domcontentloaded' });
  await p2.waitForTimeout(500);
  const r = await p2.evaluate(()=>{
    const t=document.querySelector('#layout .head-act .tb-icon');
    if (!t) return 'absent';
    return Math.round(document.documentElement.clientWidth - t.getBoundingClientRect().right);
  });
  console.log(u.padEnd(26), 'bouton theme a', r, 'px du bord droit');
}
await b.close();
