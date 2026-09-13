import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const p = await b.newPage({ viewport:{width:1280,height:900} });
const urls = ['/prix-ehpad/','/aides-ehpad/apa/','/ehpad/abbeville/','/notre-methodologie.html','/guides/','/professionnels/'];
for (const u of urls) {
  await p.goto('http://127.0.0.1:8899'+u, { waitUntil:'domcontentloaded' });
  await p.waitForTimeout(500);
  const bad = await p.evaluate(()=>[...document.querySelectorAll('h1,h2,h3,h4')]
    .map(h=>h.innerText.replace(/\s+/g,' ').trim())
    .filter(t=>/[a-zà-ÿ][A-ZÀ-Ý]/.test(t) && !/ViaTrajectoire|EHPAD|CNSA|FINESS|HAS|INSEE|DREES|CCAS|APA|ASH|MSA|CAF|IGN|PUI|GIR/.test(t)));
  console.log(u.padEnd(26), bad.length ? '⚠ ' + bad.join(' / ') : 'ok');
}
await b.close();
