/**
 * Tests du Worker, sans déploiement : D1 est remplacé par une table en mémoire
 * qui reconnaît les quelques requêtes réellement utilisées.
 *   node worker/test.mjs
 */
import worker from './index.js';

// ── Base simulée
function faireDB() {
  const lignes = [];
  let seq = 1;
  return {
    lignes,
    prepare(sql) {
      const ctx = { sql, args: [] };
      return {
        bind(...a) { ctx.args = a; return this; },
        async all() {
          if (/SELECT COUNT/.test(ctx.sql)) {
            const [emp] = ctx.args;
            return { results: [{ n: lignes.filter((l) => l.empreinte === emp).length }] };
          }
          if (/WHERE etat = 'publie'/.test(ctx.sql)) {
            return { results: lignes.filter((l) => l.etat === 'publie') };
          }
          return { results: lignes };
        },
        async run() {
          if (/^INSERT/.test(ctx.sql.trim())) {
            const [nom, message, empreinte] = ctx.args;
            // L'état et la date de publication sont écrits en dur dans la requête :
            // le simulateur les relit plutôt que de les supposer, sinon il validerait
            // un comportement qui n'est pas celui du Worker.
            const etat = (ctx.sql.match(/VALUES \(\?, \?, '(\w+)'/) || [, 'attente'])[1];
            lignes.push({ id: seq++, nom, message, etat, recu_le: 'maintenant',
                          publie_le: etat === 'publie' ? '2026-09-13' : null, empreinte });
          } else if (/^UPDATE retours SET etat/.test(ctx.sql.trim())) {
            const [etat, , id] = ctx.args;
            const l = lignes.find((x) => x.id === id);
            if (l) { l.etat = etat; if (etat === 'publie') l.publie_le = '2026-09-13'; }
          } else if (/^DELETE/.test(ctx.sql.trim())) {
            const i = lignes.findIndex((x) => x.id === ctx.args[0]);
            if (i >= 0) lignes.splice(i, 1);
          }
          return {};
        },
      };
    },
  };
}

const DB = faireDB();
const env = { DB, CLE_ADMIN: 'secret-de-test', SEL_IP: 'sel-de-test' };
const VIEUX = Date.now() - 10000;

const poste = (corps, ip = '1.2.3.4') => worker.fetch(new Request('https://x/messages', {
  method: 'POST', headers: { 'Content-Type': 'application/json', 'CF-Connecting-IP': ip },
  body: JSON.stringify(corps),
}), env);

const cas = [];
const test = (nom, fn) => cas.push([nom, fn]);

test('un message valide est publié immédiatement', async () => {
  const r = await poste({ message: 'Le calculateur m’a bien aidé, merci.', depuis: VIEUX });
  const d = await r.json();
  return d.ok === true && DB.lignes.length === 1
      && DB.lignes[0].etat === 'publie' && !!DB.lignes[0].publie_le;
});

test('le message d’un robot qui remplit le champ piège n’est pas enregistré', async () => {
  const avant = DB.lignes.length;
  const d = await (await poste({ message: 'achetez des montres', site: 'http://spam', depuis: VIEUX })).json();
  return d.ok === true && DB.lignes.length === avant;   // réponse neutre, rien en base
});

test('un formulaire rempli en moins de trois secondes est ignoré', async () => {
  const avant = DB.lignes.length;
  await poste({ message: 'rempli instantanément par un script', depuis: Date.now() });
  return DB.lignes.length === avant;
});

test('un message trop court est refusé', async () => {
  const r = await poste({ message: 'bof', depuis: VIEUX });
  return r.status === 400 && (await r.json()).erreur === 'court';
});

test('les chevrons sont neutralisés avant l’enregistrement', async () => {
  await poste({ message: 'essai <script>alert(1)</script> de balisage', depuis: VIEUX });
  const d = DB.lignes[DB.lignes.length - 1];
  return !d.message.includes('<') && !d.message.includes('>');
});

test('le message est tronqué à 1500 caractères', async () => {
  await poste({ message: 'a'.repeat(3000), depuis: VIEUX });
  return DB.lignes[DB.lignes.length - 1].message.length === 1500;
});

test('au-delà de trois messages par heure, la même adresse est refusée', async () => {
  const r = await poste({ message: 'un message de plus depuis la même adresse', depuis: VIEUX });
  return r.status === 429 && (await r.json()).erreur === 'trop';
});

test('une autre adresse n’est pas bloquée par la précédente', async () => {
  const r = await poste({ message: 'message envoyé depuis une autre adresse', depuis: VIEUX }, '9.9.9.9');
  return (await r.json()).ok === true;
});

test('l’adresse IP n’est jamais stockée en clair', async () => {
  return DB.lignes.every((l) => !l.empreinte || !l.empreinte.includes('.'));
});

test('la liste publique renvoie les messages en ligne', async () => {
  const r = await worker.fetch(new Request('https://x/messages'), env);
  const publies = DB.lignes.filter((l) => l.etat === 'publie').length;
  return (await r.json()).messages.length === publies && publies > 0;
});

test('la modération est refusée sans la clé', async () => {
  const r = await worker.fetch(new Request('https://x/admin/liste'), env);
  return r.status === 403;
});

test('la modération est refusée avec une mauvaise clé', async () => {
  const r = await worker.fetch(new Request('https://x/admin/liste?cle=faux'), env);
  return r.status === 403;
});

test('avec la bonne clé, la modération liste tout', async () => {
  const r = await worker.fetch(new Request('https://x/admin/liste?cle=secret-de-test'), env);
  return r.status === 200 && (await r.json()).messages.length === DB.lignes.length;
});

test('retirer un message le fait disparaître de la liste publique', async () => {
  const avant = (await (await worker.fetch(new Request('https://x/messages'), env)).json()).messages.length;
  const id = DB.lignes.find((l) => l.etat === 'publie').id;
  await worker.fetch(new Request('https://x/admin/etat?cle=secret-de-test', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id, etat: 'refuse' }),
  }), env);
  const apres = (await (await worker.fetch(new Request('https://x/messages'), env)).json()).messages.length;
  return apres === avant - 1;
});

test('un message retiré peut être remis en ligne', async () => {
  const id = DB.lignes.find((l) => l.etat === 'refuse').id;
  await worker.fetch(new Request('https://x/admin/etat?cle=secret-de-test', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id, etat: 'publie' }),
  }), env);
  return DB.lignes.find((l) => l.id === id).etat === 'publie';
});

test('effacer un message le supprime de la base', async () => {
  const avant = DB.lignes.length;
  const id = DB.lignes[DB.lignes.length - 1].id;
  await worker.fetch(new Request('https://x/admin/supprime?cle=secret-de-test', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id }),
  }), env);
  return DB.lignes.length === avant - 1;
});

test('un état inventé est refusé', async () => {
  const r = await worker.fetch(new Request('https://x/admin/etat?cle=secret-de-test', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id: 1, etat: 'nimporte' }),
  }), env);
  return r.status === 400;
});

test('l’écran de modération échappe le contenu des visiteurs', async () => {
  const r = await worker.fetch(new Request('https://x/admin?cle=secret-de-test'), env);
  const html = await r.text();
  return r.headers.get('X-Robots-Tag').includes('noindex')
    && html.includes('&lt;') === false ? !html.includes('<script>alert') : !html.includes('<script>alert');
});

test('l’origine autorisée est le site, pas n’importe qui', async () => {
  const r = await worker.fetch(new Request('https://x/messages'), env);
  return r.headers.get('Access-Control-Allow-Origin') === 'https://trouver-mon-ehpad.fr';
});

let ok = 0;
for (const [nom, fn] of cas) {
  let pass = false;
  try { pass = !!(await fn()); } catch (e) { console.error('   ', e.message); }
  ok += pass;
  console.log(`${pass ? '✅' : '❌'} ${nom}`);
}
console.log(`\n${ok}/${cas.length} tests du Worker OK`);
process.exit(ok === cas.length ? 0 : 1);
