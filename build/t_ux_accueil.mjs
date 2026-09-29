// Refonte de l'accueil, lot 1 (29/09/2026) : contrôles de non-régression.
// Lancer : python3 -m http.server 8899 dans site/, puis node t_ux_accueil.mjs
import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch();
let ok = 0, ko = 0;
const t = (nom, v, detail) => { if (v) ok++; else ko++; console.log((v ? '✓ ' : '✗ ') + nom + (v ? '' : '  → ' + JSON.stringify(detail))); };

for (const [w, h, nom, mob] of [[1366, 768, 'bureau', false], [390, 844, 'mobile', true]]) {
  const ctx = await b.newContext({ viewport: { width: w, height: h }, isMobile: mob, hasTouch: mob });
  await ctx.route('**/*.workers.dev/**', (r) => r.abort());
  const p = await ctx.newPage();
  const errs = []; p.on('pageerror', (e) => errs.push(e.message));
  await p.goto('http://127.0.0.1:8899/', { waitUntil: 'load' }); await p.waitForTimeout(900);
  console.log('— ' + nom);

  const d0 = await p.evaluate(() => ({
    banner: !document.getElementById('consent-banner').hidden,
    lienCookies: [...document.querySelectorAll('[data-consent-open]')].some((a) => !a.hidden && a.offsetParent),
    print: !document.getElementById('print-btn').hidden,
    cpY: Math.round(document.getElementById('cp').getBoundingClientRect().top),
    placeholders: [...document.querySelectorAll('#cp,#revenus,#epargne')].map((x) => x.placeholder).filter(Boolean),
    nav: !!document.querySelector('header nav.nav'),
    cta: document.querySelector('.tb-cta') && document.querySelector('.tb-cta').textContent.replace(/\s+/g, ' ').trim(),
    gir: window.runTests && true,
    girRes: document.getElementById('gir-res').textContent,
    rayon: !!document.getElementById('rayon'),
    prio: !!document.querySelector('[data-seg^="priorite:"]'),
    triAsh: !!document.querySelector('#tri option[value="ash"]'),
    largeur: document.documentElement.scrollWidth <= innerWidth,
  }));
  t('pas de bandeau de consentement (GTM vide)', !d0.banner, d0.banner);
  t('pas de lien « Gérer les cookies » visible', !d0.lienCookies);
  t('« Imprimer » masqué sans résultat', !d0.print);
  t('code postal dans le premier écran', d0.cpY + 48 <= h, d0.cpY);
  t('aucun placeholder sur code postal, retraite, épargne', d0.placeholders.length === 0, d0.placeholders);
  t('pastilles de navigation retirées de l’en-tête', !d0.nav);
  t('ni « Distance » ni « Ce qui compte » dans le formulaire', !d0.rayon && !d0.prio);
  t('tri « aide sociale d’abord » dans les résultats', d0.triAsh);
  t('GIR sans réponse : hypothèse annoncée', /GIR 3-4/.test(d0.girRes) && /Sans réponse/.test(d0.girRes), d0.girRes);
  t('aucun défilement horizontal', d0.largeur);
  if (!mob) t('bouton « Calculer mon reste à charge » avec son espace', /^Calculer mon reste à charge$/.test(d0.cta), d0.cta);

  // mini-grille : trois cases cochées sans que le panneau se referme
  const cases = p.locator('#gir-calc input');
  await cases.nth(0).check(); await cases.nth(1).check(); await cases.nth(2).check();
  const g1 = await p.evaluate(() => ({ gir: JSON.parse(localStorage.getItem('mon_ehpad_state_v2') || '{}').gir, res: document.getElementById('gir-res').textContent }));
  t('3 aides cochées → GIR 1-2 (la grille reste ouverte)', /GIR 1-2/.test(g1.res), g1);
  await cases.nth(4).check();
  const g2 = await p.evaluate(() => ({ coches: [...document.querySelectorAll('#gir-calc input')].map((x) => x.checked), res: document.getElementById('gir-res').textContent }));
  t('« aucune de ces aides » décoche les autres → GIR 5-6', g2.coches.join() === 'false,false,false,false,true' && /GIR 5-6/.test(g2.res), g2);
  await p.click('#gir-notif summary');
  await p.click('[data-seg^="girNotif:"] button:nth-child(2)');
  const g3 = await p.evaluate(() => ({ coches: [...document.querySelectorAll('#gir-calc input')].map((x) => x.checked), res: document.getElementById('gir-res').textContent }));
  t('GIR notifié 3-4 : grille vidée, origine dite', g3.coches.every((x) => !x) && /notifié retenu : GIR 3-4/.test(g3.res), g3);

  // saisie
  await p.fill('#cp', '69003'); await p.waitForTimeout(1200);
  const r1 = await p.evaluate(() => ({ chiffre: document.getElementById('res-chiffre').textContent, print: !document.getElementById('print-btn').hidden, affiner: !document.getElementById('affiner-btn').hidden }));
  t('sans ressources : le chiffre de tête reste le nombre d’établissements', /établissements/.test(r1.chiffre), r1);
  t('« Imprimer » visible avec un résultat', r1.print);
  t('pas d’invite à affiner sans ressources', !r1.affiner);
  await p.fill('#revenus', '1500'); await p.waitForTimeout(1200);
  const r2 = await p.evaluate(() => ({
    titre: document.getElementById('res-titre').textContent, chiffre: document.getElementById('res-chiffre').textContent,
    sous: document.getElementById('res-sous').innerText, affiner: !document.getElementById('affiner-btn').hidden,
    carte1: (document.querySelector('#liste .res .manque') || {}).textContent,
    nom1: (document.querySelector('#liste .res .res-n') || {}).textContent,
    carteVisible: !!document.getElementById('pan-carte').offsetParent,
  }));
  t('avec 1 500 € : le chiffre de tête dit ce qui manque', /il manquerait/.test(r2.titre) && /€ à .*€/.test(r2.chiffre), r2);
  t('les 150 € laissés sont écrits', /150 €\/mois pour ses dépenses personnelles/.test(r2.sous), r2.sous);
  t('la carte de résultat dit ce qui manque', /^Il manque [\d  ]+ €\/mois/.test(r2.carte1 || ''), r2.carte1);
  t('noms en casse normale', r2.nom1 && r2.nom1 !== r2.nom1.toUpperCase(), r2.nom1);
  t('invite « affiner » après le premier budget', r2.affiner);
  if (mob) {
    t('mobile : la carte est masquée par défaut', !r2.carteVisible);
    await p.click('#carte-mob'); await p.waitForTimeout(700);
    const m = await p.evaluate(() => ({ vis: !!document.getElementById('pan-carte').offsetParent, h: document.getElementById('map').getBoundingClientRect().height, marq: document.querySelectorAll('.leaflet-marker-icon').length }));
    t('mobile : « Voir sur la carte » l’affiche, avec ses marqueurs', m.vis && m.h > 200 && m.marq > 0, m);
  } else {
    t('bureau : la carte reste visible à côté de la liste', r2.carteVisible);
  }
  await p.click('#affiner-btn'); await p.waitForTimeout(500);
  t('« affiner » ouvre le bloc des précisions', await p.evaluate(() => document.getElementById('plus-situation').open));

  // pour soi-même
  await p.click('[data-seg^="pourQui:"] button:nth-child(2)');
  t('« Moi-même » : libellé d’autonomie à la 2e personne', /avez-vous besoin/.test(await p.textContent('#lbl-gir')));
  t('aucune erreur JavaScript', errs.length === 0, errs);
  await ctx.close();
}
await b.close();
console.log(`\n${ok} réussis, ${ko} en échec`);
process.exit(ko ? 1 : 0);
