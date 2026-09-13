import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const p = await b.newPage({viewport:{width:1280,height:1000}});
const errs=[]; p.on('pageerror', e=>errs.push(e.message));
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil: 'domcontentloaded' });
await p.fill('#cp','69100'); await p.fill('#revenus','1600');
await p.waitForTimeout(2500);
const lire = () => p.evaluate(()=>({
  h1: document.querySelector('h1').innerText.replace(/\n/g,' '),
  lblRev: document.getElementById('lbl-revenus')?.textContent,
  lblSit: document.getElementById('lbl-situation')?.textContent,
  nav: document.getElementById('nav-situation')?.textContent,
  sous: document.getElementById('res-sous')?.innerText.slice(0,60),
}));
console.log('AVANT', JSON.stringify(await lire()));
await p.click('[data-seg="pourQui:proche,moi"] button:nth-child(2)');
await p.waitForTimeout(1500);
console.log('APRES', JSON.stringify(await lire()));
console.log('runTests', await p.evaluate(()=>window.runTests()));
console.log('ERREURS', errs.length, errs.slice(0,3));
await b.close();
