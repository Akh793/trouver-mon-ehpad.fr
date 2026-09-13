import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const p = await b.newPage({ viewport:{width:1280,height:900} });
const errs=[]; p.on('pageerror', e=>errs.push(e.message));
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
await p.fill('#cp','69003'); await p.fill('#revenus','1600'); await p.waitForTimeout(3200);
const lire = ()=>p.evaluate(()=>({
  titre: document.getElementById('res-titre').textContent,
  premier: document.querySelector('#liste .res-n')?.textContent.slice(0,30),
  ashOnly: window.__state ? null : undefined }));
const nb = ()=>p.evaluate(()=>+(document.getElementById('res-chiffre').textContent.replace(/\s/g,'').match(/(\d+)/)||[0,0])[1]);
const avant = await nb();
for (const [i, nom] of [[0,'Le budget'],[1,'La proximité'],[2,'Les aides'],[3,'La qualité']]) {
  await p.click(`[data-seg="priorite:rac,dist,ash,has"] button:nth-child(${i+1})`);
  await p.waitForTimeout(1200);
  const n = await nb();
  const info = await lire();
  console.log(nom.padEnd(14), n, 'etablissements', n===avant?'(inchange)':'*** LA LISTE A CHANGE ***', '| 1er :', info.premier);
}
console.log('ERREURS', errs.length, errs.slice(0,3));
await b.close();
