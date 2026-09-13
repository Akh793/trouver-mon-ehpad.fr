import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const p = await b.newPage({ viewport:{width:1280,height:900} });
const ok = (c,t)=>console.log((c?'✅':'❌')+' '+t);
await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
await p.waitForTimeout(1500);
await p.evaluate(()=>{ const c=document.getElementById('consent-banner'); if(c) c.remove();
  document.querySelectorAll('#bande-faq details').forEach(d=>d.open=true); });

const d = await p.evaluate(() => {
  const items = [...document.querySelectorAll('#bande-faq .faq-i')];
  const cible = items.find(e => /revenus ne suffisent pas/.test(e.textContent));
  const a = cible && cible.querySelector('p a');
  return { nb: items.length,
    texteBrut: items.some(e => /&lt;|<[a-z]/i.test(e.querySelector('p').textContent)),
    lien: a ? { href: a.getAttribute('href'), texte: a.textContent } : null,
    fin: cible ? cible.querySelector('p').textContent.trim().slice(-20) : null };
});
ok(d.nb === 5, 'les 5 questions sont rendues');
ok(!d.texteBrut, 'aucune balise affichée en toutes lettres');
ok(d.lien && d.lien.href === '/aides-ehpad/aide-sociale-hebergement/' && d.lien.texte === 'Les conditions',
   'le lien est un vrai lien — ' + JSON.stringify(d.lien));
ok(/conditions\.$/.test(d.fin), 'la phrase se termine par un point — « …' + d.fin + ' »');

// la cible du lien existe réellement
const r = await p.request.get('http://127.0.0.1:8899/aides-ehpad/aide-sociale-hebergement/');
ok(r.status() === 200, 'la page visée répond (' + r.status() + ')');

// JSON-LD : valide, et son texte correspond au texte affiché
const ld = await p.evaluate(() => {
  const noeuds = [...document.querySelectorAll('script[type="application/ld+json"]')]
    .flatMap(x => { const d = JSON.parse(x.textContent);
      return d['@graph'] || (Array.isArray(d) ? d : [d]); });
  const s = noeuds.find(x => x['@type'] === 'FAQPage');
  const q = s.mainEntity.find(x => /revenus ne suffisent pas/.test(x.name));
  const el = [...document.querySelectorAll('#bande-faq .faq-i')]
    .find(e => /revenus ne suffisent pas/.test(e.textContent)).querySelector('p');
  return { ld: q.acceptedAnswer.text, html: el.innerHTML.replace(/\s+/g,' ').trim() };
});
ok(ld.ld.replace(/\s+/g,' ').trim() === ld.html, 'texte affiché et texte FAQPage identiques');
await b.close();
