import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
const cas = [
  { nom: 'Régime expérimental (Villeurbanne 69100)', cp:'69100', rev:'1600' },
  { nom: 'Régime de droit commun (Bordeaux 33000)', cp:'33000', rev:'1600' },
  { nom: 'Outre-mer (Fort-de-France 97200)', cp:'97200', rev:'1200' },
  { nom: 'Corse (Ajaccio 20000)', cp:'20000', rev:'1500' },
  { nom: 'Coordonnées converties (Toulouse 31300)', cp:'31300', rev:'1800' },
  { nom: 'Ressources nulles (Lille 59000)', cp:'59000', rev:'0' },
];
for (const c of cas) {
  const p = await b.newPage(); const errs=[];
  p.on('pageerror', e=>errs.push(e.message));
  await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
  await p.evaluate(()=>{try{localStorage.clear()}catch(e){}});
  await p.fill('#cp', c.cp); if (c.rev !== '0') await p.fill('#revenus', c.rev);
  await p.waitForTimeout(3200);
  const r = await p.evaluate(()=>({
    titre: document.getElementById('res-titre').textContent,
    chiffre: document.getElementById('res-chiffre').textContent,
    items: document.querySelectorAll('#liste .res').length,
    premier: document.querySelector('#liste .res-n')?.textContent,
    montant: document.querySelector('#liste .res-m b')?.textContent.trim(),
    reserve: document.querySelector('#liste .t-reserve')?.textContent || '',
  }));
  console.log(c.nom.padEnd(42), '|', r.items, 'résultats |', r.chiffre, '|', (r.premier||'').slice(0,28), r.montant||'', r.reserve?('· '+r.reserve):'', errs.length?('ERREURS '+errs[0]):'');
  await p.close();
}
await b.close();
