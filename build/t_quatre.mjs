import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
const ok = (c, t) => console.log((c ? '✅' : '❌') + ' ' + t);

// ── 1. police réellement chargée sur /retours/
{
  const p = await b.newPage({ viewport:{width:1280,height:900} });
  const err = [];
  p.on('response', r => { if (r.status() >= 400) err.push(r.url()); });
  await p.goto('http://127.0.0.1:8899/retours/', { waitUntil:'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  const fam = await p.locator('h1').evaluate(e => getComputedStyle(e).fontFamily);
  const chargees = await p.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family + ' ' + f.weight));
  ok(chargees.some(f => f.startsWith('Poppins')) && chargees.some(f => f.startsWith('Inter')),
     '1. /retours/ : Poppins et Inter chargées — ' + JSON.stringify([...new Set(chargees.map(f=>f.split(' ')[0]))]));
  ok(err.length === 0, '1b. /retours/ : aucune ressource en erreur' + (err.length ? ' — ' + err.join(', ') : ''));
  ok(/Poppins/.test(fam), '1c. /retours/ : le h1 est bien en Poppins (' + fam.split(',')[0] + ')');
  // comparaison avec une page de référence
  const p2 = await b.newPage();
  await p2.goto('http://127.0.0.1:8899/prix-ehpad/', { waitUntil:'networkidle' });
  await p2.evaluate(() => document.fonts.ready);
  const fam2 = await p2.locator('h1').evaluate(e => getComputedStyle(e).fontFamily);
  ok(fam === fam2, '1d. même famille que /prix-ehpad/ (' + fam2.split(',')[0] + ')');
  await p.close(); await p2.close();
}

// ── 2, 3, 4 sur l'accueil
{
  const p = await b.newPage({ viewport:{width:1400,height:900} });
  await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
  await p.waitForTimeout(1500);
  await p.evaluate(() => { const c = document.getElementById('consent-banner'); if (c) c.remove(); });
  const lit = e => { const c = getComputedStyle(e); return { bg:c.backgroundColor, col:c.color, bord:c.borderTopColor }; };
  const survol = async sel => {
    const el = p.locator(sel).first();
    await el.scrollIntoViewIfNeeded();
    const r = await el.evaluate(lit);
    await el.hover(); await p.waitForTimeout(350);
    const s = await el.evaluate(lit);
    await p.mouse.move(5, 5); await p.waitForTimeout(250);
    return { repos:r, surv:s };
  };
  // ouvrir le bloc des sources, qui vit dans un <details>
  await p.evaluate(() => document.querySelectorAll('#bande-sources details').forEach(d => d.open = true));

  const nav = await survol('.nav-avis');
  ok(nav.surv.col === 'rgb(255, 255, 255)' && nav.surv.bg === 'rgb(163, 93, 0)',
     '2. menu « Vos retours » au survol : blanc sur ambre profond — ' + JSON.stringify(nav.surv));
  // contraste du texte sur le fond de survol : AA demande 4,5:1 pour du petit texte
  const lum = h => { const v = [1,3,5].map(i => { const c = parseInt(h.slice(i,i+2),16)/255;
      return c <= 0.03928 ? c/12.92 : Math.pow((c+0.055)/1.055, 2.4); });
    return 0.2126*v[0] + 0.7152*v[1] + 0.0722*v[2]; };
  const ratio = (1.05) / (lum('#a35d00') + 0.05);
  ok(ratio >= 4.5, '2c. contraste du survol : ' + ratio.toFixed(2) + ':1 (AA = 4,5)');

  const g = await survol('#bande-guides .g-card');
  ok(g.surv.bg === 'rgb(246, 248, 255)' && g.surv.bord === 'rgb(199, 210, 254)',
     '3. « Pour aller plus loin » : survol bleu — ' + JSON.stringify(g.surv));

  const s = await survol('#bande-sources .non-sim li');
  ok(s.surv.bg === 'rgb(246, 248, 255)' && s.surv.bord === 'rgb(199, 210, 254)',
     '3b. « D’où viennent ces données » : survol bleu — ' + JSON.stringify(s.surv));

  const e = await survol('#bande-explorer .g-card');
  ok(e.surv.bg === 'rgb(255, 246, 244)' && e.surv.bord === 'rgb(255, 201, 189)',
     '4. « Parcourir sans calculer » : survol corail — ' + JSON.stringify(e.surv));

  ok(g.repos.bg === e.repos.bg, '4b. au repos, les deux grilles restent identiques');

  // le bouton de la barre haute n'a pas régressé
  await p.evaluate(() => window.scrollTo(0, 900)); await p.waitForTimeout(600);
  const tb = await survol('.tb-avis');
  ok(tb.surv.col === 'rgb(255, 255, 255)' && tb.surv.bg === 'rgb(224, 138, 0)',
     '2b. barre haute : toujours blanc sur orange — ' + JSON.stringify(tb.surv));
  await p.close();
}

// ── thème sombre : les teintes doivent exister aussi
{
  const p = await b.newPage({ viewport:{width:1400,height:900}, colorScheme:'dark' });
  await p.goto('http://127.0.0.1:8899/index.html', { waitUntil:'domcontentloaded' });
  await p.waitForTimeout(1200);
  const v = await p.evaluate(() => { const c = getComputedStyle(document.documentElement);
    return { co:c.getPropertyValue('--ti-co2').trim(), bd:c.getPropertyValue('--bd-co').trim() }; });
  ok(v.co && v.bd, 'sombre : teintes corail définies — ' + JSON.stringify(v));
  await p.close();
}
await b.close();
