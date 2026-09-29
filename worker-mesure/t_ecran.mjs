/** Écran d'audience : interrupteur Sombre, contraste, mémorisation. node worker-mesure/t_ecran.mjs */
import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
import worker from './index.js';
const J = [{ periode: '2026-09-29', vues: 12, engages: 8, entrees: 5, declares: 3, suspects: 1, vous: 4 }];
const DB = { prepare(sql) { return { bind() { return this; }, async all() {
  if (/AS periode/.test(sql)) return { results: J.map((x) => ({ ...x })) };
  if (/GROUP BY heure/.test(sql)) return { results: [{ heure: 9, engages: 3 }, { heure: 14, engages: 5 }] };
  if (/FROM motifs/.test(sql)) return { results: [{ motif: 'hebergeur:Google LLC', vues: 1 }] };
  return { results: [] }; } }; } };
const html = await (await worker.fetch(new Request('https://x/mesure?cle=k'), { DB, CLE_MESURE: 'k' })).text();
let ok = 0, tot = 0; const T = (c, t) => { tot++; ok += c ? 1 : 0; console.log((c ? '✅' : '❌') + ' ' + t); };
const lum = (c) => { const [r, g, b] = c.match(/\d+(\.\d+)?/g).slice(0, 3).map(Number).map((v) => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; });
  return .2126 * r + .7152 * g + .0722 * b; };
const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((m, n) => n - m); return (x + .05) / (y + .05); };
const b = await chromium.launch();
for (const schema of ['light', 'dark']) {
  const ctx = await b.newContext({ colorScheme: schema, viewport: { width: 1280, height: 900 } });
  await ctx.route('https://mesure.test/**', (r) => r.fulfill({ status: 200, contentType: 'text/html; charset=utf-8', body: html }));
  const p = await ctx.newPage(); const err = []; p.on('pageerror', (e) => err.push(e.message));
  await p.goto('https://mesure.test/mesure');
  const lire = () => p.evaluate(() => { const s = getComputedStyle(document.body), v = document.querySelector('.v'), sw = document.getElementById('sw');
    return { bg: s.backgroundColor, fg: s.color, mut: getComputedStyle(v).color, chk: sw.getAttribute('aria-checked'),
      piste: getComputedStyle(sw.querySelector('i')).backgroundColor, pouce: getComputedStyle(sw.querySelector('i'), '::after').backgroundColor,
      vis: sw.getBoundingClientRect().width > 0 }; });
  const a = await lire();
  T(a.vis && a.chk === String(schema === 'dark'), `système ${schema} : interrupteur visible, état ${a.chk}`);
  await p.click('#sw'); const c = await lire();
  T(c.chk !== a.chk && c.bg !== a.bg, `système ${schema} : un clic bascule (${a.bg} → ${c.bg})`);
  for (const [n, x] of [['avant', a], ['après', c]])
    T(ratio(x.fg, x.bg) >= 7 && ratio(x.mut, x.bg) >= 4.5 && ratio(x.piste, x.pouce) >= 3,
      `système ${schema}, ${n} clic : texte ${ratio(x.fg, x.bg).toFixed(1)}:1, gris ${ratio(x.mut, x.bg).toFixed(1)}:1, curseur ${ratio(x.piste, x.pouce).toFixed(1)}:1`);
  await p.reload(); const d = await lire();
  T(d.chk === c.chk && err.length === 0, `système ${schema} : choix conservé au rechargement, aucune erreur JS`);
  if (process.env.SHOTS) await p.screenshot({ path: `${process.env.SHOTS}/ecran-${schema}.png`, clip: { x: 0, y: 0, width: 1280, height: 420 } });
  await ctx.close();
}
await b.close(); console.log(`\n${ok}/${tot} tests de l’écran d’audience OK`); process.exit(ok === tot ? 0 : 1);
