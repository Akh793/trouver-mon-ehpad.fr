import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const p = await b.newPage({ viewport:{width:1280,height:900} });
const errs=[]; p.on('pageerror', e=>errs.push(e.message));
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
await p.fill('#cp','69003'); await p.fill('#revenus','1600'); await p.waitForTimeout(3200);
await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove(); });
console.log('liens tel :', JSON.stringify(await p.evaluate(()=>{
  const l=[...document.querySelectorAll('#liste .res-tel')];
  const c=[...document.querySelectorAll('#liste .res')];
  const a=l[0];
  const boutons=a?[...a.closest('.res-act').children].map(e=>Math.round(e.getBoundingClientRect().top)):[];
  return { cartes:c.length, avecTel:l.length, href:a?a.getAttribute('href'):null,
    texte:a?a.textContent.trim():null, memeNiveau: new Set(boutons).size===1, niveaux:boutons };
})));
// le clic ne doit pas ouvrir la fiche
const avant = await p.evaluate(()=>document.querySelectorAll('.res[aria-current="true"]').length);
await p.evaluate(()=>{ const a=document.querySelector('#liste .res-tel'); a.removeAttribute('href'); a.click(); });
await p.waitForTimeout(500);
const apres = await p.evaluate(()=>document.querySelectorAll('.res[aria-current="true"]').length);
console.log('fiche ouverte par le clic tel ?', avant, '->', apres, apres>avant ? 'OUI (bug)' : 'non');
const c = await p.$('#liste .res'); await c.scrollIntoViewIfNeeded(); await p.waitForTimeout(300);
await c.screenshot({path:'carte-tel.png'});
console.log('ERREURS', errs.length, errs.slice(0,3));
await b.close();
