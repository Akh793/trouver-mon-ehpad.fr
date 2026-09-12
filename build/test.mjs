import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
const errs = [], logs = [];
p.on('console', m => { logs.push(m.type()+': '+m.text()); if (m.type()==='error') errs.push(m.text()); });
p.on('pageerror', e => errs.push('pageerror: '+e.message));
p.on('requestfailed', r => errs.push('requestfailed: '+r.url()+' '+ (r.failure()?.errorText||'')));
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil: 'networkidle' });
// tests moteur
const res = await p.evaluate(() => window.runTests());
console.log('runTests →', res);
// saisie
await p.fill('#cp', '69003');
await p.fill('#revenus', '1600');
await p.evaluate(()=>{const d=document.getElementById('plus-situation'); if(d) d.open=true;});
await p.fill('#epargne', '40000');
await p.waitForTimeout(2500);
const info = await p.evaluate(() => ({
  titre: document.getElementById('res-titre').textContent,
  chiffre: document.getElementById('res-chiffre').textContent,
  sous: document.getElementById('res-sous').textContent.slice(0,160),
  items: document.querySelectorAll('#liste .res').length,
  marqueurs: document.querySelectorAll('.leaflet-interactive').length,
  contexte: document.getElementById('contexte').textContent.slice(0,320),
  etapes: document.querySelectorAll('#route .step').length,
  premier: document.querySelector('#liste .res-n')?.textContent,
  premierMontant: document.querySelector('#liste .res-m b')?.textContent.trim(),
}));
console.log(JSON.stringify(info, null, 1));
await p.screenshot({ path: 'shot-haut.png', fullPage: false });
await p.evaluate(() => document.getElementById('bande-carte').scrollIntoView());
await p.waitForTimeout(1200);
await p.screenshot({ path: 'shot-carte.png' });
console.log('ERREURS ('+errs.length+'):'); errs.slice(0,12).forEach(e=>console.log(' -',e));
await b.close();
