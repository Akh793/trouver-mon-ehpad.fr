import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
for (const [lib, vp] of [['bureau 1280', {width:1280,height:900}], ['mobile 390', {width:390,height:844}]]) {
  const p = await b.newPage({ viewport: vp });
  await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
  await p.fill('#cp','69003'); await p.fill('#revenus','1600');
  await p.waitForTimeout(3200);
  const r = await p.evaluate(()=>{
    const h = (s)=>{const e=document.querySelector(s); if(!e) return null; const b=e.getBoundingClientRect();
      return {h:Math.round(b.height), w:Math.round(b.width)};};
    const opt = document.querySelector('.share-opt');
    return { share: h('#share-btn'), rouge: h('#action-rouge'), opt: h('.share-opt'),
      couleur: opt ? getComputedStyle(opt).color : null,
      dansTa: opt ? opt.closest('.t-a') !== null : null };
  });
  console.log(lib.padEnd(12), JSON.stringify(r));
  await p.screenshot({path:`barre-${vp.width}.png`, clip:{x:0,y:0,width:vp.width,height:Math.min(900,vp.height)}});
  await p.close();
}
await b.close();
