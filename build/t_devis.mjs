import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const ok = (c,t)=>{ console.log((c?'✅':'❌')+' '+t); return c?1:0; };
let n=0, tot=0;
const T=(c,t)=>{ tot++; n+=ok(c,t); };
const b = await chromium.launch();
const ctx = await b.newContext({ viewport:{width:1400,height:1000} });
const p = await ctx.newPage();
const err=[]; p.on('pageerror',e=>err.push(e.message));
p.on('console',m=>{ if(m.type()==='error') err.push('console: '+m.text()); });
await p.goto('http://127.0.0.1:8899/comparer-devis-ehpad/', { waitUntil:'networkidle' });
await p.waitForTimeout(500);

T(err.length===0, 'aucune erreur JS au chargement'+(err.length?' — '+err.join(' | '):''));
T(await p.locator('h1').first().textContent().then(t=>/Comparer vos devis/.test(t)), 'titre H1');
T((await p.locator('.pr-l').count())===9, '9 prestations de la liste CNSA ('+(await p.locator('.pr-l').count())+')');
T(await p.locator('#dv-vide').isVisible(), 'état vide affiché tant que rien n’est saisi');

// --- saisie du premier devis
await p.fill('#dv-nom','Résidence Alpha');
await p.fill('#dv-heb','74.22');
await p.click('[data-f="incl"][data-v="non"]');
await p.fill('#dv-talon','6.55');
await p.waitForTimeout(250);
const t1 = await p.locator('.dv-c .dv-m').first().textContent();
// 74,22 + 6,55 = 80,77 €/j × 30,4167 = 2457 €
T(/2\s?4[56]\d/.test(t1.replace(/ | /g,' ')), 'total mensuel calculé en base 365/12 — '+t1.split('par')[0].trim());
T(!(await p.locator('#dv-vide').isVisible()), 'l’état vide disparaît');

// --- la question décisive change bien le total
await p.click('[data-f="incl"][data-v="oui"]');
await p.waitForTimeout(200);
const t2 = await p.locator('.dv-c .dv-m').first().textContent();
T(t1!==t2, '« dépendance comprise » change le total ('+t1.split('par')[0].trim()+' → '+t2.split('par')[0].trim()+')');
await p.click('[data-f="incl"][data-v="non"]');

// --- prestation en sus (l'étape 2 est repliée par défaut : c'est voulu)
T(!(await p.locator('.pr-l[data-p="coi"] [data-v="sus"]').isVisible()),
  'l’étape 2 est repliée au départ — la page ne s’ouvre pas sur 9 lignes');
await p.evaluate(()=>document.querySelector('.et-d[data-et="2"]').open = true);
await p.waitForTimeout(200);
await p.click('.pr-l[data-p="coi"] [data-v="sus"]');
await p.waitForTimeout(150);
T(await p.locator('.pr-l[data-p="coi"] .pr-p').isVisible(), 'choisir « en plus » ouvre le champ de prix');
await p.fill('.pr-l[data-p="coi"] .pr-p input','25');
await p.waitForTimeout(250);
const t3 = await p.locator('.dv-c .dv-m').first().textContent();
T(t3!==t1, 'une prestation en sus entre dans le total');
T((await p.locator('#dv-c2').textContent()).startsWith('1 sur 9'), 'le compteur d’étape suit la saisie');

// --- garde-fous légaux
await p.evaluate(()=>document.querySelector('.et-d[data-et="3"]').open = true);
await p.waitForTimeout(150);
await p.fill('#dv-caution','9000');
await p.waitForTimeout(200);
T((await p.locator('#dv-caution-a').getAttribute('class')||'').includes('bad'),
  'dépôt de garantie au-delà d’un mois : signalé');
await p.fill('#dv-caution','');
await p.fill('#dv-deces','15');
await p.waitForTimeout(200);
T((await p.locator('#dv-deces-a').textContent()).includes('6 jours'),
  'facturation après décès au-delà de 6 jours : signalée');
await p.fill('#dv-deces','');

// --- régime déduit du territoire
await p.fill('#dv-cp','19000');          // Corrèze : territoire en fusion
await p.waitForTimeout(1500);
T(await p.locator('#dv-dep-exp').isVisible(), 'code postal en territoire fusionné → bloc forfaitaire');
T(!(await p.locator('#dv-dep-cl').isVisible()), '… et la grille GIR disparaît');
T((await p.locator('#dv-forf').inputValue())==='6.16', 'forfait 2026 pré-rempli à 6,16 €');
await p.fill('#dv-cp','75001');          // Paris : régime classique
await p.waitForTimeout(1500);
T(await p.locator('#dv-dep-cl').isVisible(), 'code postal en régime classique → grille GIR');
T((await p.locator('#dv-etab option').count())>1, 'liste des établissements du code postal chargée');

// --- deuxième devis et comparaison
await p.click('#dv-add');
await p.waitForTimeout(200);
await p.fill('#dv-nom','Résidence Beta');
await p.fill('#dv-heb','66.29');
await p.click('[data-f="incl"][data-v="non"]');
await p.fill('#dv-talon','6.05');
await p.waitForTimeout(300);
T((await p.locator('.dv-c').count())===2, 'deux devis comparés côte à côte');
T((await p.locator('.dv-c.min').count())===1, 'le moins cher est distingué');
T((await p.locator('.dv-c-b').first().textContent())==='le moins cher', 'étiquette explicite');
T((await p.locator('.dv-tab tbody tr').count())>=4, 'tableau poste par poste rendu');
T((await p.locator('.dv-d.plus').count())===1, 'écart mensuel et annuel affiché sur l’autre devis');

// --- l'avertissement de comparabilité
const alerte = await p.locator('#dv-alerte').textContent();
T(/comparables/.test(alerte), 'bandeau de comparabilité : « ces devis sont comparables »');
await p.click('[data-f="chambre"][data-v="cd"]');
await p.waitForTimeout(300);
T(/partagée/.test(await p.locator('#dv-alerte').textContent()),
  'chambre individuelle vs partagée : incomparabilité signalée');
await p.click('[data-f="chambre"][data-v="cs"]');

// --- persistance locale
await p.reload({ waitUntil:'networkidle' }); await p.waitForTimeout(600);
T((await p.locator('.dv-o').count())===2, 'la saisie survit au rechargement');
T((await p.locator('#dv-nom').inputValue())==='Résidence Beta', '… y compris le devis actif');

// --- remise à zéro
await p.click('#dv-raz'); await p.waitForTimeout(300);
T((await p.locator('.dv-o').count())===1 && (await p.locator('#dv-heb').inputValue())==='', 'tout effacer fonctionne');

// --- accessibilité et responsive
const a11y = await p.evaluate(()=>{
  const sansLabel=[...document.querySelectorAll('input,select')].filter(e=>{
    if(e.closest('.sr')) return false;
    return !e.labels?.length && !e.getAttribute('aria-label') && !e.closest('label');
  }).length;
  const seg=[...document.querySelectorAll('.seg[role="radiogroup"]')];
  const segOk=seg.every(g=>[...g.querySelectorAll('button')].every(b=>b.hasAttribute('aria-checked')));
  return { sansLabel, segOk, h1:document.querySelectorAll('h1').length,
           imgNoAlt:[...document.images].filter(i=>!i.alt&&i.alt!=='').length };
});
T(a11y.sansLabel===0, 'aucun champ sans intitulé ('+a11y.sansLabel+')');
T(a11y.segOk, 'tous les interrupteurs portent aria-checked');
T(a11y.h1===1, 'un seul h1');

// On remplit de nouveau : le tableau comparatif est l'élément le plus large,
// c'est lui qui révèle un débordement.
await p.fill('#dv-heb','74.22'); await p.click('[data-f="incl"][data-v="non"]');
await p.fill('#dv-talon','6.55'); await p.waitForTimeout(300);
for (const w of [1400,1024,900,700,390]) {
  await p.setViewportSize({width:w,height:900});
  await p.waitForTimeout(300);
  // scrollWidth ne suffit pas : #layout porte overflow-x:clip, qui masque le
  // débordement au lieu de le faire défiler. On mesure les bords réels, en
  // excluant la barre haute du site, antérieure à cette page.
  const d = await p.evaluate(()=>{
    const vw = document.documentElement.clientWidth, bad = [];
    document.querySelectorAll('#layout *').forEach(e=>{
      const r = e.getBoundingClientRect();
      if (r.width && r.right > vw + 1 && !e.closest('.dv-tab-w'))
        bad.push(e.tagName.toLowerCase()+'.'+String(e.className).split(' ')[0]+' → '+Math.round(r.right));
    });
    return bad.slice(0,3);
  });
  T(d.length===0, w+'px : aucun élément ne déborde'+(d.length?' — '+d.join(', '):''));
}
T(err.length===0, 'aucune erreur JS sur l’ensemble du parcours'+(err.length?' — '+err.join(' | '):''));

console.log('\n'+n+'/'+tot+' tests de la page devis OK');
await b.close();
process.exit(n===tot?0:1);
