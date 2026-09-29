/** Écran d'audience : interrupteur Sombre et graphique « Visites par jour ».  node worker-mesure/t_ecran.mjs */
import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
import worker, { quand } from './index.js';

const AUJ = quand(new Date()).jour;
const jourMoins = (k) => new Date(Date.parse(AUJ + 'T00:00:00Z') - k * 86400000).toISOString().slice(0, 10);
// 400 jours d'historique, un jour sur trois sans aucune ligne (trou à combler), pic connu il y a 11 jours
const LIGNES = [];
for (let k = 399; k >= 0; k--) if (k % 3 !== 1) LIGNES.push({ jour: jourMoins(k), e: k === 11 ? 57 : (k % 7), c: k === 11 ? 80 : (k % 7) + 3 });
const PREMIER = jourMoins(399);
// profil horaire : pic à 14 h sur « Tout », pic à 21 h sur 30 jours, rien la nuit
const HEURES = Array.from({ length: 24 }, (_, h) => h < 7 ? null : ({ heure: h,
  e30: h === 21 ? 12 : 1, c30: h === 21 ? 15 : 2, e90: h === 21 ? 20 : 3, c90: 25, e365: h === 14 ? 90 : 10, c365: 120,
  et: h === 14 ? 140 : 12, ct: h === 14 ? 170 : 18 })).filter(Boolean);
const J = [{ periode: AUJ, vues: 12, engages: 8, entrees: 5, declares: 3, suspects: 1, vous: 4 }];
const faireDB = (lignes, premier) => ({ prepare(sql) { return { bind() { return this; }, async all() {
  if (/AS periode/.test(sql)) return { results: J.map((x) => ({ ...x })) };
  if (/MIN\(jour\)/.test(sql)) return { results: [{ premier }] };
  if (/GROUP BY jour ORDER BY jour/.test(sql)) return { results: lignes.map((x) => ({ ...x })) };
  if (/GROUP BY heure/.test(sql)) return { results: HEURES.map((x) => ({ ...x })) };
  if (/FROM motifs/.test(sql)) return { results: [{ motif: 'hebergeur:Google LLC', vues: 1 }] };
  return { results: [] }; } }; } });
const page = async (lignes, premier) => (await worker.fetch(new Request('https://x/mesure?cle=k'),
  { DB: faireDB(lignes, premier), CLE_MESURE: 'k' })).text();

let ok = 0, tot = 0; const T = (c, t) => { tot++; ok += c ? 1 : 0; console.log((c ? '✅' : '❌') + ' ' + t); };
const lum = (c) => { const [r, g, b] = c.match(/\d+(\.\d+)?/g).slice(0, 3).map(Number).map((v) => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; });
  return .2126 * r + .7152 * g + .0722 * b; };
const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((m, n) => n - m); return (x + .05) / (y + .05); };
const b = await chromium.launch();
async function ouvrir(html, opts = {}) {
  const ctx = await b.newContext({ viewport: { width: 1280, height: 900 }, ...opts });
  await ctx.route('https://mesure.test/**', (r) => r.fulfill({ status: 200, contentType: 'text/html; charset=utf-8', body: html }));
  const p = await ctx.newPage(); const err = []; p.on('pageerror', (e) => err.push(e.message));
  await p.goto('https://mesure.test/mesure'); await p.waitForTimeout(150);
  return { ctx, p, err };
}
const HTML = await page(LIGNES, PREMIER);

// ── 1. Interrupteur Sombre
for (const schema of ['light', 'dark']) {
  const { ctx, p, err } = await ouvrir(HTML, { colorScheme: schema });
  const lire = () => p.evaluate(() => { const s = getComputedStyle(document.body), v = document.querySelector('.v'), sw = document.getElementById('sw');
    const barre = document.querySelector('#graphe .b'), ligne = document.querySelector('#graphe .lc');
    return { bg: s.backgroundColor, fg: s.color, mut: getComputedStyle(v).color, chk: sw.getAttribute('aria-checked'),
      piste: getComputedStyle(sw.querySelector('i')).backgroundColor, pouce: getComputedStyle(sw.querySelector('i'), '::after').backgroundColor,
      barre: getComputedStyle(barre).fill, ligne: getComputedStyle(ligne).stroke, vis: sw.getBoundingClientRect().width > 0 }; });
  const a = await lire();
  T(a.vis && a.chk === String(schema === 'dark'), `système ${schema} : interrupteur visible, état ${a.chk}`);
  await p.click('#sw'); const c = await lire();
  T(c.chk !== a.chk && c.bg !== a.bg, `système ${schema} : un clic bascule (${a.bg} → ${c.bg})`);
  for (const [n, x] of [['avant', a], ['après', c]])
    T(ratio(x.fg, x.bg) >= 7 && ratio(x.mut, x.bg) >= 4.5 && ratio(x.piste, x.pouce) >= 3 && ratio(x.barre, x.bg) >= 3 && ratio(x.ligne, x.bg) >= 3,
      `système ${schema}, ${n} clic : texte ${ratio(x.fg, x.bg).toFixed(1)}, gris ${ratio(x.mut, x.bg).toFixed(1)}, curseur ${ratio(x.piste, x.pouce).toFixed(1)}, barres ${ratio(x.barre, x.bg).toFixed(1)}, courbe ${ratio(x.ligne, x.bg).toFixed(1)} (:1)`);
  await p.reload(); await p.waitForTimeout(150); const d = await lire();
  T(d.chk === c.chk && err.length === 0, `système ${schema} : choix conservé au rechargement, aucune erreur JS`);
  if (process.env.SHOTS) await p.screenshot({ path: `${process.env.SHOTS}/ecran-${schema}.png`, fullPage: false });
  await ctx.close();
}

// ── 2. Graphique
{
  const { ctx, p, err } = await ouvrir(HTML);
  const etat = () => p.evaluate(() => { const g = document.querySelector('#graphe svg');
    return { barres: g.querySelectorAll('.b').length, pale: g.querySelectorAll('.b.auj').length, ligne: !!g.querySelector('.lc'),
      moy: !!g.querySelector('.lm'), legMoy: !!document.querySelector('#gleg .mo'), label: g.getAttribute('aria-label'),
      presse: [...document.querySelectorAll('#fenj button')].filter((x) => x.getAttribute('aria-pressed') === 'true').map((x) => x.textContent),
      ax: [...g.querySelectorAll('text.ax')].map((t) => t.textContent) }; });
  const attendu = (n) => LIGNES.filter((l) => l.jour >= jourMoins(n - 1) && l.e > 0).length;
  let e = await etat();
  const jSer = JSON.parse(await p.textContent('#gdata')).jours;
  T(jSer.length === 400 && jSer[0][0] === PREMIER && jSer[399][0] === AUJ && jSer.filter((x) => x[1] === 0 && x[2] === 0).length >= 133,
    `« Tout » par défaut : 400 jours continus du ${PREMIER} à aujourd’hui, trous remplis de zéros`);
  T(e.presse.join() === 'Tout' && e.barres === attendu(400) && e.ligne && e.moy && e.legMoy,
    `« Tout » : ${e.barres} barres (jours à visites), courbe des chargements, moyenne 7 j affichée au-delà de 120 jours`);
  T(/maximum 57 le/.test(e.label), 'résumé lisible par lecteur d’écran : total et maximum (' + e.label.slice(0, 70) + '…)');
  T(e.ax.some((t) => /^(janv|févr|mars|avr|mai|juin|juil|août|sept|oct|nov|déc)/.test(t)), 'au-delà de 120 jours : axe gradué par mois');
  await p.click('#fenj button[data-f="30"]'); e = await etat();
  T(e.presse.join() === '30 j' && e.barres === attendu(30) && !e.moy && !e.legMoy && e.ax.some((t) => /^\d\d\/\d\d$/.test(t)),
    `« 30 j » : ${e.barres} barres, pas de moyenne, dates jj/mm`);
  T(e.ax.includes(AUJ.slice(8) + '/' + AUJ.slice(5, 7)), 'le jour le plus récent est étiqueté sur l’axe');
  // survol du pic (il y a 10 jours) → infobulle exacte
  const pos = await p.evaluate(() => { const g = document.querySelector('#graphe svg'), r = g.getBoundingClientRect(),
    W = +g.getAttribute('viewBox').split(' ')[2], sl = (W - 40 - 10) / 30; return { x: r.left + (40 + (18 + .5) * sl) * r.width / W, y: r.top + 120 }; });
  await p.mouse.move(pos.x, pos.y); await p.waitForTimeout(80);
  const tip = await p.evaluate(() => { const t = document.getElementById('gtip'), r = t.getBoundingClientRect(), g = document.getElementById('graphe').getBoundingClientRect();
    return { txt: t.innerText, vis: getComputedStyle(t).display !== 'none', dans: r.left >= g.left - 1 && r.right <= g.right + 1 }; });
  T(tip.vis && /Visites engagées : 57/.test(tip.txt) && /Chargements : 80/.test(tip.txt) && tip.dans, 'survol du pic : infobulle « 57 engagées / 80 chargements », dans le cadre');
  await p.mouse.move(pos.x + 2000, pos.y); await p.mouse.move(10, 10); await p.waitForTimeout(50);
  // clavier
  await p.focus('#graphe svg'); await p.keyboard.press('End');
  let t2 = await p.textContent('#gtip');
  T(/en cours/.test(t2), 'clavier : Fin → aujourd’hui, marqué « en cours »');
  await p.keyboard.press('ArrowLeft'); t2 = await p.textContent('#gtip');
  T(!/en cours/.test(t2) && /Visites engagées/.test(t2), 'clavier : flèche gauche → la veille');
  await p.keyboard.press('Escape');
  T(await p.evaluate(() => getComputedStyle(document.getElementById('gtip')).display === 'none'), 'Échap masque l’infobulle');
  T(e.pale === 1 || !LIGNES.find((l) => l.jour === AUJ && l.e > 0), 'journée en cours en barre pâle');
  // largeur de téléphone
  await p.setViewportSize({ width: 360, height: 800 }); await p.waitForTimeout(250);
  const mob = await p.evaluate(() => { const g = document.querySelector('#graphe svg').getBoundingClientRect();
    const labs = [...document.querySelectorAll('#graphe text.ax')].map((t) => t.getBoundingClientRect()).filter((r) => r.top > g.top + 200).sort((a, b) => a.left - b.left);
    let chev = false; for (let i = 1; i < labs.length; i++) if (labs[i].left < labs[i - 1].right) chev = true;
    return { w: g.width, sw: document.documentElement.scrollWidth, vw: innerWidth, chev, n: labs.length,
      fen: Math.max(...[...document.querySelectorAll('.fen')].map((f) => f.getBoundingClientRect().right)) }; });
  T(mob.sw <= mob.vw && mob.fen <= mob.vw && !mob.chev && mob.n >= 2,
    `360 px : graphique redessiné à la largeur (${Math.round(mob.w)} px), ${mob.n} dates sans chevauchement, aucun débordement ${JSON.stringify(mob)}`);
  T(err.length === 0, 'aucune erreur JavaScript');
  // ── Heures de consultation
  await p.setViewportSize({ width: 1280, height: 900 }); await p.waitForTimeout(250);
  const hEtat = () => p.evaluate(() => { const g = document.querySelector('#gheures svg');
    return { barres: g.querySelectorAll('.b').length, ligne: !!g.querySelector('.lc'), label: g.getAttribute('aria-label'),
      ax: [...g.querySelectorAll('text.ax')].map((t) => t.textContent).filter((t) => / h$/.test(t)),
      presse: [...document.querySelectorAll('#fenh button')].filter((x) => x.getAttribute('aria-pressed') === 'true').map((x) => x.textContent),
      jourPresse: [...document.querySelectorAll('#fenj button')].filter((x) => x.getAttribute('aria-pressed') === 'true').map((x) => x.textContent) }; });
  let h = await hEtat();
  T(h.presse.join() === 'Tout' && h.barres === 17 && h.ligne && /pic entre 14 h et 15 h avec 140/.test(h.label),
    `heures, « Tout » : 17 barres (7 h → 23 h), courbe des chargements, pic 14 h annoncé (${h.label.slice(0, 60)}…)`);
  T(h.ax[0] === '0 h' && h.ax.length >= 8, `heures : axe de 0 h à 23 h (${h.ax.join(' ')})`);
  await p.click('#fenh button[data-f="30"]'); h = await hEtat();
  T(h.presse.join() === '30 j' && /pic entre 21 h et 22 h avec 12/.test(h.label) && h.jourPresse.join() === '30 j',
    'heures, « 30 j » : pic déplacé à 21 h ; les boutons de chaque graphique sont indépendants');
  await p.focus('#gheures svg'); await p.keyboard.press('Home'); for (let i = 0; i < 21; i++) await p.keyboard.press('ArrowRight');
  const ht = await p.textContent('#htip');
  T(/21 h – 22 h/.test(ht) && /Visites engagées : 12/.test(ht) && /Chargements : 15/.test(ht) && /\(\d+ %\)/.test(ht),
    'heures, clavier : 21 h – 22 h → 12 engagées (part du total en %), 15 chargements');
  await p.keyboard.press('Escape');
  await p.setViewportSize({ width: 360, height: 800 }); await p.waitForTimeout(250);
  const hm = await p.evaluate(() => { const labs = [...document.querySelectorAll('#gheures text.ax')].filter((t) => / h$/.test(t.textContent)).map((t) => t.getBoundingClientRect());
    let chev = false; for (let i = 1; i < labs.length; i++) if (labs[i].left < labs[i - 1].right) chev = true;
    return { chev, n: labs.length, sw: document.documentElement.scrollWidth, vw: innerWidth }; });
  T(!hm.chev && hm.n >= 4 && hm.sw <= hm.vw, `heures, 360 px : ${hm.n} graduations sans chevauchement, aucun débordement`);
  await p.click('#fenh button[data-f="tout"]');
  if (process.env.SHOTS) { await p.setViewportSize({ width: 1100, height: 900 }); await p.waitForTimeout(200);
    const g = await p.$('#gheures'); const bb = await g.boundingBox();
    await p.mouse.move(700, bb.y + 110); await p.waitForTimeout(80);
    await p.screenshot({ path: `${process.env.SHOTS}/heures.png`, clip: { x: 0, y: bb.y - 90, width: 1100, height: bb.height + 150 } }); }
  T(err.length === 0, 'heures : aucune erreur JavaScript');
  if (process.env.SHOTS) { await p.setViewportSize({ width: 1100, height: 900 }); await p.click('#fenj button[data-f="tout"]'); await p.waitForTimeout(200);
    const g = await p.$('#graphe'); const bb = await g.boundingBox();
    await p.screenshot({ path: `${process.env.SHOTS}/graphe-tout.png`, clip: { x: 0, y: bb.y - 90, width: 1100, height: bb.height + 150 } });
    await p.click('#fenj button[data-f="30"]'); await p.waitForTimeout(200);
    await p.mouse.move(600, bb.y + 120); await p.waitForTimeout(80);
    await p.screenshot({ path: `${process.env.SHOTS}/graphe-30.png`, clip: { x: 0, y: bb.y - 90, width: 1100, height: bb.height + 150 } }); }
  await ctx.close();
}
// ── 3. Base neuve : un seul jour, à zéro
{
  const { ctx, p, err } = await ouvrir(await page([], null));
  const r = await p.evaluate(() => ({ svg: !!document.querySelector('#graphe svg'), b: document.querySelectorAll('#graphe .b').length,
    pt: !!document.querySelector('#graphe .pc'), ax: [...document.querySelectorAll('#graphe text.ax')].map((t) => t.textContent) }));
  T(r.svg && r.b === 0 && r.pt && r.ax.includes('0') && err.length === 0, 'base vide : graphique à zéro pour aujourd’hui, sans erreur');
  await ctx.close();
}
await b.close(); console.log(`\n${ok}/${tot} tests de l’écran d’audience OK`); process.exit(ok === tot ? 0 : 1);
