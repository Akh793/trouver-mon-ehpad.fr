import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const p = await b.newPage({viewport:{width:1280,height:900}});
await p.goto('http://127.0.0.1:8899/index.html',{waitUntil:'networkidle'});
await p.fill('#cp','69003'); await p.fill('#revenus','1600'); await p.waitForTimeout(2500);
const a = await p.evaluate(()=>{
  const hs=[...document.querySelectorAll('h1,h2,h3,h4')].map(h=>+h.tagName[1]);
  let saut=null; for(let i=1;i<hs.length;i++) if(hs[i]-hs[i-1]>1) saut=hs[i-1]+'→'+hs[i];
  const noLabel=[...document.querySelectorAll('input,select')].filter(el=>!el.labels?.length && !el.getAttribute('aria-label')).length;
  // alt="" est l'écriture correcte d'une image décorative (les tuiles Leaflet, par exemple).
  // Ne compter que les images SANS attribut alt : sinon le contrôle signale 15 faux positifs.
  const imgNoAlt=[...document.querySelectorAll('img')].filter(i=>!i.hasAttribute('alt')).length;
  return {main:!!document.querySelector('main'), h1:document.querySelectorAll('h1').length, saut, noLabel, imgNoAlt,
    lang:document.documentElement.lang, titre:document.title.length};
});
console.log(JSON.stringify(a));
await p.evaluate(()=>window.scrollTo(0,0)); await p.waitForTimeout(300);
await p.screenshot({path:'final-haut.png'});
await p.evaluate(()=>document.getElementById('bande-carte').scrollIntoView()); await p.waitForTimeout(1500);
await p.screenshot({path:'final-carte.png'});
await p.evaluate(()=>document.getElementById('bande-route').scrollIntoView()); await p.waitForTimeout(600);
await p.screenshot({path:'final-route.png'});
await b.close();
