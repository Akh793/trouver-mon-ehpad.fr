/**
 * Marque « propriétaire » (#ne-pas-me-compter) et interrupteur du mode sombre,
 * sur les pages RECONSTRUITES servies en local (PAGE_BASE, port 8911 par défaut).
 * Le réseau vers le Worker est intercepté : rien ne part réellement.
 */
import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const BASE = process.env.PAGE_BASE || 'http://127.0.0.1:8911';
const SHOTS = process.env.SHOTS || '';
const CHROME = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36';
let ok = 0, tot = 0; const T = (c, t) => { tot++; ok += c ? 1 : 0; console.log((c ? '✅' : '❌') + ' ' + t); };
const b = await chromium.launch();

async function contexte(vp = { width: 1280, height: 800 }) {
  const ctx = await b.newContext({ userAgent: CHROME, viewport: vp });
  const recu = [];
  await ctx.route('**/*.workers.dev/**', async (r) => { const u = new URL(r.request().url());
    if (u.host.startsWith('mesure-tme')) recu.push(Object.fromEntries(u.searchParams)); await r.fulfill({ status: 204 }); });
  await ctx.addInitScript(() => { Object.defineProperty(Navigator.prototype, 'webdriver', { get: () => false });
    if (!window.chrome) window.chrome = { runtime: {} }; });
  return { ctx, recu };
}
async function visite(ctx, recu, chemin) {
  recu.length = 0; const p = await ctx.newPage(); const err = [];
  p.on('pageerror', (e) => err.push(e.message));
  await p.goto(BASE + chemin, { waitUntil: 'domcontentloaded' }); await p.waitForTimeout(400);
  await p.mouse.wheel(0, 300); await p.waitForTimeout(300);
  return { p, err };
}

// ── 1. Marque propriétaire
{
  const { ctx, recu } = await contexte();
  let { p, err } = await visite(ctx, recu, '/#ne-pas-me-compter');
  const toast = await p.locator('[role=status]', { hasText: 'colonne « Vous »' }).isVisible();
  const etat = await p.evaluate(() => ({ h: location.hash, f: localStorage.getItem('tme_proprio') }));
  T(toast && etat.h === '' && etat.f === '1', 'lien #ne-pas-me-compter : message affiché, ancre retirée, marque posée');
  T(recu.length === 2 && recu.every((q) => q.m === '1'), 'chargement et engagement partent avec m=1');
  T(err.length === 0, 'aucune erreur JavaScript');
  await p.close();
  ({ p } = await visite(ctx, recu, '/ehpad/lyon/'));
  T(recu.length === 2 && recu.every((q) => q.m === '1') && !(await p.locator('[role=status]', { hasText: 'Vous' }).count()),
    'page suivante : m=1, sans message');
  await p.close();
  ({ p } = await visite(ctx, recu, '/comparer-devis-ehpad/#ne-plus-m-exclure'));
  const f2 = await p.evaluate(() => localStorage.getItem('tme_proprio'));
  T(f2 === null && recu.length === 2 && recu.every((q) => !('m' in q)) &&
    await p.locator('[role=status]', { hasText: 'visiteur ordinaire' }).isVisible(),
    'lien #ne-plus-m-exclure : marque retirée, visites de nouveau ordinaires');
  await ctx.close();
}
{
  const { ctx, recu } = await contexte();
  const { p } = await visite(ctx, recu, '/');
  const cles = await p.evaluate(() => Object.keys(localStorage));
  T(recu.length === 2 && recu.every((q) => !('m' in q)) && !cles.includes('tme_proprio'),
    'visiteur ordinaire : pas de m, rien d’écrit dans son navigateur (' + cles.join(',') + ')');
  await ctx.close();
}

// ── 2. Interrupteur du mode sombre
const lum = (c) => { const [r, g, bl] = c.match(/\d+(\.\d+)?/g).slice(0, 3).map(Number).map((v) => { v /= 255;
  return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }); return 0.2126 * r + 0.7152 * g + 0.0722 * bl; };
const ratio = (a, c) => { const [x, y] = [lum(a), lum(c)].sort((m, n) => n - m); return (x + 0.05) / (y + 0.05); };

for (const vp of [{ width: 1280, height: 800 }, { width: 390, height: 800 }, { width: 320, height: 700 }]) {
  for (const chemin of ['/', '/ehpad/lyon/', '/retours/', '/comparer-devis-ehpad/', '/mentions-legales.html']) {
    const { ctx, recu } = await contexte(vp);
    const { p, err } = await visite(ctx, recu, chemin);
    await p.evaluate(() => window.scrollTo(0, 0)); await p.waitForTimeout(200);
    // bouton de l'en-tête (celui de la barre de défilement porte l'id theme-btn)
    const sw = p.locator('.js-theme:not(#theme-btn)');
    const info = await sw.evaluate((e) => { const r = e.getBoundingClientRect();
      const piste = e.querySelector('.sw-piste'), pouce = e.querySelector('.sw-pouce');
      return { role: e.getAttribute('role'), nom: e.getAttribute('aria-label'), txt: e.querySelector('.sw-txt').innerText,
        g: r.left, d: r.right, h: r.height, vw: innerWidth, sw: document.documentElement.scrollWidth,
        cp: getComputedStyle(piste).backgroundColor, cq: getComputedStyle(pouce).backgroundColor,
        chk: e.getAttribute('aria-checked'), dark: document.documentElement.getAttribute('data-theme') === 'dark' }; });
    const etiq = `${vp.width}px ${chemin}`;
    T(info.role === 'switch' && info.nom === 'Mode sombre' && info.txt === 'Sombre' && info.chk === String(info.dark),
      `${etiq} : interrupteur « Sombre » visible, état ARIA juste`);
    T(info.g >= 0 && info.d <= info.vw && info.sw <= info.vw && info.h >= 24,
      `${etiq} : dans l'écran, sans débordement, cible ≥ 24 px (${Math.round(info.g)}→${Math.round(info.d)}/${info.vw}, h ${info.h})`);
    const c1 = ratio(info.cp, info.cq);
    if (SHOTS) await p.screenshot({ path: `${SHOTS}/sw-${vp.width}-${chemin.replace(/\W/g, '_')}-clair.png`, clip: { x: 0, y: 0, width: vp.width, height: 200 } });
    await sw.click(); await p.waitForTimeout(300);
    const apres = await sw.evaluate((e) => ({ chk: e.getAttribute('aria-checked'),
      dark: document.documentElement.getAttribute('data-theme') === 'dark',
      cp: getComputedStyle(e.querySelector('.sw-piste')).backgroundColor,
      cq: getComputedStyle(e.querySelector('.sw-pouce')).backgroundColor,
      tx: new DOMMatrix(getComputedStyle(e.querySelector('.sw-pouce')).transform).m41 }));
    const c2 = ratio(apres.cp, apres.cq);
    T(apres.dark !== info.dark && apres.chk === String(apres.dark) && (apres.dark ? apres.tx > 10 : apres.tx < 1),
      `${etiq} : un clic bascule le thème, le curseur et aria-checked`);
    T(c1 >= 3 && c2 >= 3, `${etiq} : contraste curseur/piste ${c1.toFixed(1)}:1 et ${c2.toFixed(1)}:1 (≥ 3)`);
    if (SHOTS) await p.screenshot({ path: `${SHOTS}/sw-${vp.width}-${chemin.replace(/\W/g, '_')}-sombre.png`, clip: { x: 0, y: 0, width: vp.width, height: 200 } });
    await p.reload({ waitUntil: 'domcontentloaded' }); await p.waitForTimeout(200);
    const garde = await p.evaluate(() => document.documentElement.getAttribute('data-theme') === 'dark');
    T(garde === apres.dark && err.length === 0, `${etiq} : choix conservé au rechargement, aucune erreur JS`);
    // barre qui apparaît au défilement : même interrupteur, même contrôle d'emprise
    await p.mouse.wheel(0, 1600); await p.waitForTimeout(700);
    const tb = p.locator('#theme-btn');
    if (await tb.count() && await tb.isVisible()) {
      const r = await tb.evaluate((e) => { const q = e.getBoundingClientRect();
        return { g: q.left, d: q.right, vw: innerWidth, sw: document.documentElement.scrollWidth, chk: e.getAttribute('aria-checked'),
          dark: document.documentElement.getAttribute('data-theme') === 'dark' }; });
      await tb.click(); await p.waitForTimeout(250);
      const bas = await p.evaluate(() => document.documentElement.getAttribute('data-theme') === 'dark');
      T(r.g >= 0 && r.d <= r.vw && r.sw <= r.vw && r.chk === String(r.dark) && bas !== r.dark,
        `${etiq} : barre de défilement — interrupteur dans l'écran et fonctionnel (${Math.round(r.g)}→${Math.round(r.d)}/${r.vw})`);
      if (SHOTS) await p.screenshot({ path: `${SHOTS}/sw-${vp.width}-${chemin.replace(/\W/g, '_')}-barre.png`, clip: { x: 0, y: 0, width: vp.width, height: 90 } });
    } else T(true, `${etiq} : pas de barre de défilement affichée sur cette page`);
    await ctx.close();
  }
}
await b.close();
console.log(`\n${ok}/${tot} tests marque propriétaire + interrupteur OK`);
process.exit(ok === tot ? 0 : 1);
