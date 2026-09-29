/**
 * Tests de l'extrait de relevé dans un vrai navigateur.
 * La page de test sert l'extrait actif pointant vers http://127.0.0.1:8901 ;
 * le réseau est intercepté : on observe ce que le navigateur envoie réellement.
 */
import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
const PAGE = process.env.PAGE || 'http://127.0.0.1:8902/index.html';
let ok = 0, tot = 0;
const T = (c, t) => { tot++; ok += c ? 1 : 0; console.log((c ? '✅' : '❌') + ' ' + t); };

const b = await chromium.launch();
// Agent d'un Chrome de bureau ordinaire. Le Chromium sans écran de Playwright
// annonce « HeadlessChrome » : une session « humaine » qui le garderait serait,
// à juste titre, signalée par la règle B2.
const CHROME = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36';
async function session({ humain = false, init = '', ua } = {}) {
  const ctx = await b.newContext({ userAgent: ua || (humain ? CHROME : undefined) });
  const recu = [];
  await ctx.route('http://127.0.0.1:8901/**', async (r) => {
    const u = new URL(r.request().url());
    recu.push(Object.fromEntries(u.searchParams));
    await r.fulfill({ status: 204 });
  });
  // « Humain » : on retire les deux signes qu'un Chromium piloté porte malgré lui.
  if (humain) await ctx.addInitScript(() => {
    Object.defineProperty(Navigator.prototype, 'webdriver', { get: () => false });
    if (!window.chrome) window.chrome = { runtime: {} };
  });
  if (init) await ctx.addInitScript(init);
  const p = await ctx.newPage();
  return { ctx, p, recu };
}
const attend = (ms) => new Promise((r) => setTimeout(r, ms));

// 1. B1 — Playwright EST un navigateur automatisé : il doit être signalé.
{ const { ctx, p, recu } = await session();
  await p.goto(PAGE); await attend(500);
  const c = recu.find((x) => x.t === 'c');
  T(c && (Number(c.a) & 1) === 1, 'B1 : Playwright est détecté comme automatisé (a=' + (c && c.a) + ')');
  await ctx.close(); }

// 2. Un humain : aucun signe d'automatisation, un chargement, pas encore d'engagement.
{ const { ctx, p, recu } = await session({ humain: true });
  await p.goto(PAGE + '?cp=69003&revenus=1600#total'); await attend(500);
  const c = recu.filter((x) => x.t === 'c'), g = recu.filter((x) => x.t === 'g');
  T(c.length === 1 && c[0].a === '0', 'humain : un chargement, a=0');
  T(g.length === 0, 'B3 : aucun engagement avant le moindre geste');
  T(c[0].p === '/index.html' && !JSON.stringify(recu).includes('1600'), 'la chaîne de requête n’est jamais transmise');
  T(c[0].e === '1', 'arrivée directe comptée comme entrée');
  // 3. Geste → un seul engagement, même après plusieurs gestes.
  await p.mouse.wheel(0, 600); await attend(200);
  await p.mouse.click(50, 50); await p.keyboard.press('ArrowDown'); await attend(300);
  const g2 = recu.filter((x) => x.t === 'g');
  T(g2.length === 1 && g2[0].a === '0', 'B3 : le premier geste envoie UN engagement, pas un par geste');
  await ctx.close(); }

// 4. Engagement par la durée : 10 s d'onglet visible, sans aucun geste.
{ const { ctx, p, recu } = await session({ humain: true });
  await p.goto(PAGE); await attend(4000);
  T(!recu.some((x) => x.t === 'g'), 'B3 : pas d’engagement après 4 s immobile');
  await attend(7000);
  T(recu.filter((x) => x.t === 'g').length === 1, 'B3 : engagement après 10 s d’onglet visible');
  await ctx.close(); }

// 5. B4 — onglet ouvert en arrière-plan : rien tant qu'il n'est pas affiché.
{ const init = `(() => { let v = 'hidden';
    Object.defineProperty(Document.prototype, 'visibilityState', { get: () => v, configurable: true });
    window.__montre = () => { v = 'visible'; document.dispatchEvent(new Event('visibilitychange')); }; })()`;
  const { ctx, p, recu } = await session({ humain: true, init });
  await p.goto(PAGE); await attend(1500);
  T(recu.length === 0, 'B4 : onglet jamais affiché → rien n’est envoyé');
  await p.evaluate(() => window.__montre()); await attend(400);
  T(recu.filter((x) => x.t === 'c').length === 1, 'B4 : l’onglet s’affiche → le chargement part');
  await ctx.close(); }

// 6. B4 — pré-rendu : rien tant que la page n'est pas activée.
{ const init = `(() => { let pr = true;
    Object.defineProperty(Document.prototype, 'prerendering', { get: () => pr, configurable: true });
    window.__active = () => { pr = false; document.dispatchEvent(new Event('prerenderingchange')); }; })()`;
  const { ctx, p, recu } = await session({ humain: true, init });
  await p.goto(PAGE); await attend(1500);
  T(recu.length === 0, 'B4 : page pré-rendue → rien n’est envoyé');
  await p.evaluate(() => window.__active()); await attend(400);
  T(recu.filter((x) => x.t === 'c').length === 1, 'B4 : page activée → le chargement part');
  await ctx.close(); }

// 7. B2 — agent HeadlessChrome.
{ const { ctx, p, recu } = await session({ humain: true,
    ua: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 HeadlessChrome/140.0 Safari/537.36' });
  await p.goto(PAGE); await attend(500);
  const c = recu.find((x) => x.t === 'c');
  T(c && (Number(c.a) & 2) === 2, 'B2 : « HeadlessChrome » signalé (a=' + (c && c.a) + ')');
  await ctx.close(); }

// 8. Faux positif évité : vue intégrée Android (lien ouvert depuis Facebook,
//    WhatsApp…), agent Chrome mais sans window.chrome.
{ const init = `delete window.chrome; Object.defineProperty(window, 'chrome', { get: () => undefined });`;
  const ua = 'Mozilla/5.0 (Linux; Android 14; Pixel 8; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/140.0 Mobile Safari/537.36';
  const ctx = await b.newContext({ userAgent: ua }); const recu = [];
  await ctx.route('http://127.0.0.1:8901/**', async (r) => {
    recu.push(Object.fromEntries(new URL(r.request().url()).searchParams)); await r.fulfill({ status: 204 }); });
  await ctx.addInitScript(() => Object.defineProperty(Navigator.prototype, 'webdriver', { get: () => false }));
  await ctx.addInitScript(init);
  const p = await ctx.newPage(); await p.goto(PAGE); await attend(500);
  const c = recu.find((x) => x.t === 'c');
  T(c && (Number(c.a) & 4) === 0, 'vue intégrée Android : PAS signalée comme automatisée (a=' + (c && c.a) + ')');
  await ctx.close(); }

// 9. Un navigateur Chrome sans window.chrome (hors vue intégrée) : bit 4.
{ const init = `Object.defineProperty(window, 'chrome', { get: () => undefined, configurable: true });`;
  const ctx = await b.newContext({ userAgent: CHROME }); const recu = [];
  await ctx.route('http://127.0.0.1:8901/**', async (r) => {
    recu.push(Object.fromEntries(new URL(r.request().url()).searchParams)); await r.fulfill({ status: 204 }); });
  await ctx.addInitScript(() => Object.defineProperty(Navigator.prototype, 'webdriver', { get: () => false }));
  await ctx.addInitScript(init);
  const p = await ctx.newPage(); await p.goto(PAGE); await attend(500);
  const c = recu.find((x) => x.t === 'c');
  T(c && c.a === '4', 'B2 : agent Chrome sans objet window.chrome signalé (a=' + (c && c.a) + ')');
  await ctx.close(); }

// 10. Service injoignable : la page ne casse pas.
{ const ctx = await b.newContext(); const err = [];
  await ctx.route('http://127.0.0.1:8901/**', (r) => r.abort());
  const p = await ctx.newPage(); p.on('pageerror', (e) => err.push(e.message));
  await p.goto(PAGE); await p.mouse.wheel(0, 500); await attend(800);
  T(err.length === 0 && (await p.locator('h1').textContent()) === 'Test', 'service injoignable : aucune erreur, la page s’affiche');
  await ctx.close(); }

await b.close();
console.log(`\n${ok}/${tot} tests de l’extrait OK`);
process.exit(ok === tot ? 0 : 1);
