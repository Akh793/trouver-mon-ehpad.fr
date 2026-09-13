import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const p = await b.newPage({ viewport:{width:1440,height:1100} });
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove();
                       document.getElementById('plus-situation').open = true; });
await p.waitForTimeout(900);
console.log(JSON.stringify(await p.evaluate(()=>{
  return [...document.querySelectorAll('.grid4 .fld')].filter(e=>e.offsetParent).map(c=>{
    const lab=c.querySelector('label'), ctrl=c.querySelector('input,select,.seg,.in-eur');
    const cs=getComputedStyle(ctrl), ls=getComputedStyle(lab);
    return { label: lab.textContent.slice(0,22), hLabel: Math.round(lab.getBoundingClientRect().height),
      ctrl: ctrl.className||ctrl.tagName, mt: cs.marginTop,
      yCtrl: Math.round(ctrl.getBoundingClientRect().top - c.getBoundingClientRect().top) };
  });
}), null, 1));
await b.close();
