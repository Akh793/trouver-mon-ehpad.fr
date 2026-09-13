import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
const etats = [
  ['premiere visite',        async p=>{}],
  ['code postal seul',       async p=>{ await p.fill('#cp','69003'); }],
  ['commune a choisir',      async p=>{ await p.fill('#cp','01500'); }],
  ['situation partielle',    async p=>{ await p.fill('#cp','69003'); await p.fill('#revenus','1600'); }],
  ['GIR inconnu',            async p=>{ await p.fill('#cp','69003'); await p.fill('#revenus','1600');
                                        await p.click('[data-seg^="gir:"] button:nth-child(4)'); }],
  ['couple deux residents',  async p=>{ await p.fill('#cp','69003'); await p.fill('#revenus','1600');
                                        await p.evaluate(()=>{document.getElementById('plus-situation').open=true;});
                                        await p.click('[data-seg="couple:false,true"] button:nth-child(2)');
                                        await p.waitForTimeout(400);
                                        await p.click('[data-seg="deuxResidents:false,true"] button:nth-child(2)'); }],
  ['aide sociale exigee',    async p=>{ await p.fill('#cp','69003'); await p.fill('#revenus','900');
                                        await p.click('[data-seg="besoinAsh:nsp,oui,non"] button:nth-child(2)').catch(()=>{}); }],
  ['aucun resultat',         async p=>{ await p.fill('#cp','69003'); await p.evaluate(()=>{
                                        window.__f=1; }); await p.selectOption('#rayon','10');
                                        await p.click('[data-check="hasAB"]').catch(()=>{}); }],
  ['regime experimental',    async p=>{ await p.fill('#cp','69100'); await p.fill('#revenus','1600'); }],
  ['ressources nulles',      async p=>{ await p.fill('#cp','59000'); }],
];
for (const [nom, prep] of etats) {
  const p = await b.newPage({ viewport:{width:1280,height:1000} });
  const errs=[]; p.on('pageerror', e=>errs.push(e.message));
  await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
  await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
  try { await prep(p); } catch(e) { }
  await p.waitForTimeout(3000);
  const r = await p.evaluate(()=>({
    chiffre: document.getElementById('res-chiffre')?.textContent.trim(),
    sous: (document.getElementById('res-sous')?.textContent||'').slice(0,100),
    items: document.querySelectorAll('#liste .res').length,
  }));
  console.log(nom.padEnd(22), '|', String(r.chiffre).padEnd(20), '|', r.items, 'cartes |', errs.length?('ERREUR '+errs[0].slice(0,50)):'ok');
  await p.close();
}
await b.close();
