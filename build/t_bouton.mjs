import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
for (const w of [1440, 1280, 1024, 900, 860, 700, 390]) {
  const p = await b.newPage({ viewport:{width:w,height:900}, isMobile:w<500 });
  await p.goto('http://127.0.0.1:8899/', { waitUntil:'domcontentloaded' });
  await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
  // faire apparaitre la barre du haut
  await p.evaluate(()=>window.scrollTo(0, 600)); await p.waitForTimeout(600);
  console.log(w, JSON.stringify(await p.evaluate(()=>{
    const a=document.querySelector('.tb-avis'), cta=document.querySelector('.tb-cta');
    const menu=[...document.querySelectorAll('#tb-menu a')].some(x=>x.getAttribute('href')==='/retours/');
    const de=document.documentElement;
    const vis=(e)=>e && getComputedStyle(e).display!=='none';
    return { boutonBarre: vis(a), dansMenu: menu,
      ctaTronque: cta ? cta.scrollWidth > cta.clientWidth+1 : null,
      debordement: de.scrollWidth > de.clientWidth };
  })));
  await p.close();
}
// capture de la barre
const p2 = await b.newPage({ viewport:{width:1280,height:900} });
await p2.goto('http://127.0.0.1:8899/', { waitUntil:'domcontentloaded' });
await p2.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
await p2.evaluate(()=>window.scrollTo(0,600)); await p2.waitForTimeout(800);
const tb = await p2.$('#topbar'); await tb.screenshot({path:'b-topbar.png'});
await p2.evaluate(()=>window.scrollTo(0,0)); await p2.waitForTimeout(600);
const nv = await p2.$('header .nav'); await nv.screenshot({path:'b-nav.png'});
await b.close();
