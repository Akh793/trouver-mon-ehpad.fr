import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
const p = await b.newPage({ viewport:{width:390,height:844}, isMobile:true, hasTouch:true, deviceScaleFactor:2 });
const errs=[]; p.on('pageerror', e=>errs.push(e.message));
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
await p.fill('#cp','69100'); await p.fill('#revenus','1600');
await p.waitForTimeout(3500);
const r = await p.evaluate(()=>{
  const de=document.documentElement;
  // éléments qui débordent horizontalement
  const large=[...document.querySelectorAll('body *')].filter(e=>{
    const r=e.getBoundingClientRect(); return r.width>de.clientWidth+2 && r.height>0;
  }).slice(0,6).map(e=>e.tagName+'.'+(e.className||'').toString().slice(0,30)+' w='+Math.round(e.getBoundingClientRect().width));
  // conteneurs qui défilent à l'intérieur de la page (défilement imbriqué)
  const nest=[...document.querySelectorAll('body *')].filter(e=>{
    const st=getComputedStyle(e);
    return /auto|scroll/.test(st.overflowY) && e.scrollHeight>e.clientHeight+8 && e.clientHeight>80;
  }).map(e=>e.tagName+'.'+(e.className||'').toString().slice(0,40)+' h='+e.clientHeight+'/'+e.scrollHeight);
  return { largeurDoc: de.scrollWidth, largeurVue: de.clientWidth, deborde: large, imbrique: nest,
           items: document.querySelectorAll('#liste .res').length };
});
console.log(JSON.stringify(r,null,1));
console.log('ERREURS', errs.length, errs.slice(0,3));
await p.screenshot({path:'mobile-haut.png'});
await b.close();
