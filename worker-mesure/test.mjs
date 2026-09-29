/**
 * Tests du compteur, sans déploiement : D1 est remplacé par une table en mémoire.
 *   node worker-mesure/test.mjs
 */
import worker, { quand, chemin, domaine, estDeclare, estHebergeur, classe,
                 HUMAIN, DECLARE, SUSPECT, PROPRIO, HORS_LISTE } from './index.js';

function faireDB() {
  const t = { vues: [], motifs: [], sources: [], pays: [] };
  const cles = { vues: 4, motifs: 2, sources: 2, pays: 2 };
  function prepare(sql) {
    const ctx = { sql, args: [] };
    return {
      bind(...a) { ctx.args = a; return this; },
      async run() {
        const m = /^INSERT INTO (\w+)/.exec(ctx.sql.trim()); if (!m) return {};
        const nom = m[1], a = ctx.args, k = a.slice(0, cles[nom]).join('|');
        let l = t[nom].find((x) => x.__k === k);
        if (nom === 'vues') {
          const eng = /VALUES \(\?, \?, \?, \?, 0, 1, 0\)/.test(ctx.sql);
          if (!l) { l = { __k: k, jour: a[0], heure: a[1], chemin: a[2], classe: a[3], vues: 0, engages: 0, entrees: 0 }; t.vues.push(l); }
          if (eng) l.engages++; else { l.vues++; l.entrees += a[4]; }
        } else {
          if (!l) { l = { __k: k, a: a.slice(0, cles[nom]), n: 0 }; t[nom].push(l); }
          l.n++;
        }
        return {};
      },
      async all() { return { results: [] }; },
    };
  }
  return { t, prepare, async batch(l) { for (const x of l) await x.run(); return []; } };
}

const DB = faireDB();
const env = { DB, CLE_MESURE: 'cle-de-test' };
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140 Safari/537.36';
const GOOGLE = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)';
const ORIG = 'https://trouver-mon-ehpad.fr';
const ORANGE = { country: 'FR', asn: 3215, asOrganization: 'Orange S.A.' };

const req = (q, { ua = UA, origin = ORIG, cf = ORANGE } = {}) => {
  const h = { 'User-Agent': ua }; if (origin) h.Origin = origin;
  return worker.fetch(Object.assign(new Request('https://x/v?' + q, { method: 'POST', headers: h }), { cf }), env);
};
const ligne = (c, cl) => DB.t.vues.find((l) => l.chemin === c && l.classe === cl);

const cas = []; const test = (n, f) => cas.push([n, f]);

// ── classement
test('un visiteur ordinaire est classé humain', async () => {
  const r = await req('t=c&p=/prix-ehpad/&e=1');
  const l = ligne('/prix-ehpad/', HUMAIN);
  return r.status === 204 && l && l.vues === 1 && l.entrees === 1 && l.engages === 0;
});
test('le geste humain incrémente « engagés » sur la même ligne', async () => {
  await req('t=g&p=/prix-ehpad/');
  const l = ligne('/prix-ehpad/', HUMAIN);
  return l.vues === 1 && l.engages === 1;
});
test('Googlebot est « déclaré », jamais mêlé aux humains', async () => {
  await req('t=c&p=/prix-ehpad/&e=1', { ua: GOOGLE, cf: { asn: 15169, asOrganization: 'GOOGLE' } });
  return ligne('/prix-ehpad/', DECLARE).vues === 1 && ligne('/prix-ehpad/', HUMAIN).vues === 1;
});
test('déclaré l’emporte sur hébergeur : l’information la plus sûre gagne', () =>
  classe({ ua: GOOGLE, auto: 0, cf: { asn: 15169 }, origine: ORIG }).c === DECLARE);
test('navigateur automatisé (B1/B2) → suspect, motif avec la règle', async () => {
  await req('t=c&p=/guides/&a=1');
  const m = DB.t.motifs.find((x) => x.a[1] === 'auto:1');
  return ligne('/guides/', SUSPECT).vues === 1 && !!m;
});
test('réseau d’hébergeur par numéro (OVH 16276) → suspect', () =>
  estHebergeur({ asn: 16276, asOrganization: 'OVH SAS' }) && classe({ ua: UA, auto: 0, cf: { asn: 16276 }, origine: ORIG }).c === SUSPECT);
test('réseau d’hébergeur par nom (Hetzner) → suspect', () =>
  estHebergeur({ asn: 99999, asOrganization: 'Hetzner Online GmbH' }));
test('fournisseurs d’accès grand public restent humains', () =>
  [['Orange S.A.', 3215], ['Societe Francaise Du Radiotelephone - SFR SA', 15557],
   ['Free SAS', 12322], ['Bouygues Telecom SA', 5410]]
    .every(([o, n]) => !estHebergeur({ asn: n, asOrganization: o })));
test('OVH Télécom (accès grand public, autre numéro) n’est pas pris pour l’hébergeur', () =>
  !estHebergeur({ asn: 35540, asOrganization: 'OVH Telecom' }));
test('le relais privé d’Apple (Akamai, Cloudflare, Fastly) reste humain', () =>
  [['Akamai Technologies, Inc.', 36183], ['Cloudflare, Inc.', 13335], ['Fastly, Inc.', 54113]]
    .every(([o, n]) => !estHebergeur({ asn: n, asOrganization: o })));
test('le motif hébergeur est journalisé avec le nom du réseau', async () => {
  await req('t=c&p=/guides/', { cf: { asn: 14061, asOrganization: 'DigitalOcean, LLC' } });
  return DB.t.motifs.some((x) => x.a[1] === 'hebergeur:DigitalOcean, LLC');
});

// ── origine (C1)
test('requête venue d’un autre site : ignorée, rien n’est écrit', async () => {
  const avant = JSON.stringify(DB.t);
  const r = await req('t=c&p=/prix-ehpad/', { origin: 'https://site-malveillant.example' });
  return r.status === 204 && JSON.stringify(DB.t) === avant;
});
test('requête sans origine : gardée, mais suspecte', async () => {
  await req('t=c&p=/aides-ehpad/', { origin: null });
  return ligne('/aides-ehpad/', SUSPECT).vues === 1 && DB.t.motifs.some((x) => x.a[1] === 'sans-origine');
});
test('le sous-domaine www est accepté comme origine', async () => {
  await req('t=c&p=/aides-ehpad/apa/', { origin: 'https://www.trouver-mon-ehpad.fr' });
  return !!ligne('/aides-ehpad/apa/', HUMAIN);
});

// ── chemins (C2)
test('chemin du sitemap : compté à son nom', () => chemin('/prix-ehpad/') === '/prix-ehpad/');
test('chemin inventé : rangé dans « hors-liste »', () =>
  chemin('/wp-admin/') === HORS_LISTE && chemin('/ehpad/nimporte/quoi/') === HORS_LISTE);
test('/index.html est ramené à /', () => chemin('/index.html') === '/');
test('la chaîne de requête et l’ancre ne sont jamais conservées', () =>
  chemin('/?cp=69003&revenus=1600#total') === '/');
test('une adresse inventée ne pollue pas le classement des pages', async () => {
  await req('t=c&p=/wp-login.php');
  return !DB.t.vues.some((l) => l.chemin === '/wp-login.php') && !!ligne(HORS_LISTE, HUMAIN);
});

// ── tables annexes
test('les sources et les pays ne comptent que les humains', async () => {
  await req('t=c&p=/guides/&e=1&r=google.fr', { ua: GOOGLE });
  await req('t=c&p=/guides/&e=1&r=qwant.com');
  return !DB.t.sources.some((s) => s.a[1] === 'google.fr') && DB.t.sources.some((s) => s.a[1] === 'qwant.com');
});
test('un engagement n’écrit ni source, ni pays, ni motif', async () => {
  const avant = [DB.t.sources.length, DB.t.pays.length, DB.t.motifs.length].join();
  await req('t=g&p=/guides/&r=bing.com&e=1', { origin: null });
  return [DB.t.sources.length, DB.t.pays.length, DB.t.motifs.length].join() === avant;
});

// ── garanties conservées
test('aucune adresse IP n’est enregistrée', async () => {
  await worker.fetch(Object.assign(new Request('https://x/v?t=c&p=/', { method: 'POST',
    headers: { 'User-Agent': UA, Origin: ORIG, 'CF-Connecting-IP': '203.0.113.9' } }), { cf: ORANGE }), env);
  return !/\b\d{1,3}(\.\d{1,3}){3}\b/.test(JSON.stringify(DB.t));
});
test('jour et heure de Paris, pas UTC', () => {
  const a = quand(new Date('2026-12-31T23:30:00Z')), b = quand(new Date('2026-07-01T22:30:00Z'));
  return a.jour === '2027-01-01' && a.heure === 0 && b.jour === '2026-07-02' && b.heure === 0;
});
test('un agent vide est un robot déclaré', () => estDeclare('') && estDeclare(null));
test('le masque est borné : une valeur fabriquée ne casse rien', async () => {
  const r = await req('t=c&p=/&a=999999'); return r.status === 204;
});
test('une panne de base ne fait jamais échouer la page', async () => {
  const r = await worker.fetch(new Request('https://x/v?t=c&p=/', { method: 'POST', headers: { Origin: ORIG } }),
    { DB: { prepare() { throw new Error('panne'); } } });
  return r.status === 204;
});
test('l’écran de mesure est fermé sans la clé', async () =>
  (await worker.fetch(new Request('https://x/mesure'), env)).status === 403);
// ── propriétaire du site (lien #ne-pas-me-compter)
test('navigateur marqué : chargement et engagement rangés dans « Vous »', async () => {
  const annexes = () => DB.t.sources.length + DB.t.pays.length + DB.t.motifs.length;
  const humains = () => { const h = ligne('/guides/', HUMAIN); return h ? h.vues + h.engages : 0; };
  const avant = annexes(), h0 = humains();
  await req('t=c&p=/guides/&e=1&r=google.fr&m=1'); await req('t=g&p=/guides/&m=1');
  const l = ligne('/guides/', PROPRIO);
  return l && l.vues === 1 && l.engages === 1 && humains() === h0 && annexes() === avant;
});
test('marque propriétaire ignorée sans origine (appel fabriqué)', () =>
  classe({ ua: UA, auto: 0, cf: ORANGE, origine: null, proprio: true }).c === SUSPECT);
test('marque propriétaire ignorée pour un robot déclaré', () =>
  classe({ ua: GOOGLE, auto: 0, cf: ORANGE, origine: ORIG, proprio: true }).c === DECLARE);
test('m=0 ou absent : visiteur ordinaire', () =>
  classe({ ua: UA, auto: 0, cf: ORANGE, origine: ORIG, proprio: false }).c === HUMAIN);
test('domaine référent normalisé', () => domaine('WWW.Google.fr') === 'google.fr');

let ok = 0;
for (const [n, f] of cas) { let p = false; try { p = !!(await f()); } catch (e) { console.error('   ', e.message); }
  ok += p; console.log(`${p ? '✅' : '❌'} ${n}`); }
console.log(`\n${ok}/${cas.length} tests du compteur OK`);
process.exit(ok === cas.length ? 0 : 1);
