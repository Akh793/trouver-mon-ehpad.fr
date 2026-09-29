/**
 * Chaîne complète : l'extrait dans un vrai navigateur envoie ses requêtes au
 * VRAI code du Worker (base en mémoire). On vérifie la classe finale obtenue.
 * L'origine est réécrite en celle du site : la page de test est servie en local.
 */
import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js'; const { chromium } = pkg;
import worker, { HUMAIN, DECLARE, SUSPECT } from '../worker-mesure/index.js';

const lignes = [], motifs = [];
const DB = { prepare(sql) { const c = { sql, a: [] }; return {
  bind(...a) { c.a = a; return this; },
  async run() { if (/^INSERT INTO vues/.test(c.sql.trim())) lignes.push({ chemin: c.a[2], classe: c.a[3], eng: /0, 1, 0\)/.test(c.sql) });
    if (/^INSERT INTO motifs/.test(c.sql.trim())) motifs.push(c.a[1]); return {}; } }; },
  async batch(l) { for (const x of l) await x.run(); } };
const env = { DB };
const CHROME = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36';
let ok = 0, tot = 0; const T = (c, t) => { tot++; ok += c ? 1 : 0; console.log((c ? '✅' : '❌') + ' ' + t); };

const b = await chromium.launch();
// mode : 'brut' (UA HeadlessChrome), 'masque' (UA Chrome normal mais webdriver vrai), 'humain'
async function visite(mode) {
  const humain = mode === 'humain';
  const ctx = await b.newContext(mode === 'brut' ? {} : { userAgent: CHROME });
  await ctx.route('http://127.0.0.1:8901/**', async (r) => {
    const req = new Request(r.request().url(), { method: 'POST',
      headers: { 'User-Agent': r.request().headers()['user-agent'], Origin: 'https://trouver-mon-ehpad.fr' } });
    await worker.fetch(Object.assign(req, { cf: { country: 'FR', asn: 3215, asOrganization: 'Orange S.A.' } }), env);
    await r.fulfill({ status: 204 });
  });
  if (humain) await ctx.addInitScript(() => {
    Object.defineProperty(Navigator.prototype, 'webdriver', { get: () => false });
    if (!window.chrome) window.chrome = { runtime: {} }; });
  const p = await ctx.newPage();
  await p.goto('http://127.0.0.1:8902/index.html'); await p.waitForTimeout(400);
  await p.mouse.wheel(0, 500); await p.waitForTimeout(400);
  await ctx.close();
}

lignes.length = 0; motifs.length = 0; await visite('brut');
T(lignes.length === 2 && lignes.every((l) => l.classe === DECLARE),
  'Playwright brut (UA « HeadlessChrome ») : chargement ET engagement rangés parmi les DÉCLARÉS');
T(lignes.every((l) => l.chemin === '/'), '/index.html ramené au chemin « / » du sitemap');

lignes.length = 0; motifs.length = 0; await visite('masque');
T(lignes.length === 2 && lignes.every((l) => l.classe === SUSPECT),
  'robot à UA maquillé (webdriver vrai) : chargement ET engagement rangés parmi les SUSPECTS');
T(motifs.length === 1 && /^auto:\d+$/.test(motifs[0]) && (parseInt(motifs[0].slice(5)) & 1) === 1,
  'motif enregistré une fois, avec le drapeau webdriver (' + motifs.join(',') + ')');

lignes.length = 0; motifs.length = 0; await visite('humain');
T(lignes.length === 2 && lignes.every((l) => l.classe === HUMAIN),
  'navigateur au profil humain : chargement et engagement comptés HUMAINS');
T(lignes.filter((l) => l.eng).length === 1, 'un seul engagement pour la visite');
T(motifs.length === 0, 'aucun motif de suspicion pour la visite humaine');

await b.close();
console.log(`\n${ok}/${tot} tests de la chaîne complète OK`);
process.exit(ok === tot ? 0 : 1);
