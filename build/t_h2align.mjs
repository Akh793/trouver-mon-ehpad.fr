import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
for (const w of [1440, 1280, 900, 600, 390]) {
  const p = await b.newPage({ viewport:{width:w,height:1000}, isMobile:w<500 });
  await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
  await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
  await p.waitForTimeout(900);
  console.log(w, JSON.stringify(await p.evaluate(()=>
    [...document.querySelectorAll('h2:has(.n)')].map(h=>{
      const n=h.querySelector('.n'), t=h.querySelector('.t');
      const rn=n.getBoundingClientRect(), rt=t.getBoundingClientRect();
      return { txt:t.textContent.slice(0,16),
        lignes: Math.round(rt.height/parseFloat(getComputedStyle(t).lineHeight)),
        gouttiere: Math.round(rt.left - rn.right),
        ecartCentre: Math.round((rn.top+rn.height/2)-(rt.top+rt.height/2)) };
    })
  )));
  await p.close();
}
await b.close();
