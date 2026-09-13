import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
const p = await b.newPage({ viewport:{width:1280,height:900} });
const errs=[]; p.on('pageerror', e=>errs.push(e.message));
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
await p.waitForTimeout(1200);
console.log(JSON.stringify(await p.evaluate(()=>{
  const mots=(t)=>(String(t).match(/\S+/g)||[]).length;
  const h=document.querySelector('header');
  return { h1: document.querySelector('h1').innerText.replace(/\n/g,' '),
    sub: document.querySelector('.sub').innerText.replace(/\n/g,' '),
    motsHeader: mots(h.innerText) - mots(document.querySelector('header nav').innerText),
    perfVisible: !!document.getElementById('perf'),
    vraiment: (document.body.innerText.match(/vraiment|réel|réelle/gi)||[]).length };
}), null, 1));
await p.screenshot({path:'r-haut.png', clip:{x:0,y:0,width:1280,height:560}});
console.log('ERREURS', errs.length, errs.slice(0,3));
await b.close();
