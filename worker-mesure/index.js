/**
 * Compteur d'audience de trouver-mon-ehpad.fr — Worker séparé.
 *
 * Séparé du service de retours : le plan gratuit alloue 100 000 requêtes par
 * jour, et un pic de trafic ne doit pas empêcher un visiteur de déposer un message.
 *
 * Ce que le service reçoit : un chemin, un type d'évènement (chargement ou
 * engagement), un drapeau d'entrée, un domaine référent, et un indicateur de
 * navigateur automatisé calculé dans la page. Ce qu'il lit lui-même : l'agent
 * utilisateur, l'en-tête Origin, le réseau d'origine et le pays fournis par
 * Cloudflare. Ce qu'il n'écrit jamais : l'IP, la chaîne de requête, un identifiant.
 *
 * Chaque vue est rangée dans une classe — humain, robot déclaré, suspect — et
 * n'est jamais jetée : une vue mal classée se reclasse, une vue jetée est perdue.
 * Seule exception : une requête qui vient d'un AUTRE site est ignorée, car elle
 * ne décrit aucune visite de ce site.
 */
import { CHEMINS } from './chemins.js';

const SITE = 'trouver-mon-ehpad.fr';
const ORIGINES = new Set(['https://' + SITE, 'https://www.' + SITE]);
export const HUMAIN = 0, DECLARE = 1, SUSPECT = 2;
export const HORS_LISTE = '/(hors-liste)';

// ── Jour et heure de Paris. En UTC, une visite à 1 h serait comptée la veille.
const HORLOGE = new Intl.DateTimeFormat('en-CA', {
  timeZone: 'Europe/Paris', year: 'numeric', month: '2-digit', day: '2-digit',
  hour: '2-digit', hour12: false,
});
export function quand(date) {
  const p = {};
  for (const m of HORLOGE.formatToParts(date)) p[m.type] = m.value;
  return { jour: `${p.year}-${p.month}-${p.day}`, heure: Number(p.hour) % 24 };
}

// ── Robots qui s'annoncent. Un agent vide est traité comme tel : aucun
//    navigateur réel n'envoie une requête sans agent utilisateur.
const ROBOT = /bot|crawl|spider|slurp|scrap|fetcher|monitor|preview|headless|phantom|lighthouse|pingdom|gtmetrix|curl|wget|python-requests|okhttp|java\/|go-http|libwww|semrush|ahrefs|mj12|dotbot|petal|bytespider|gptbot|claudebot|ccbot|perplexity|applebot|yandex|baidu|facebookexternalhit|embedly/i;
export const estDeclare = (ua) => !ua || ROBOT.test(String(ua));

// ── Réseaux d'hébergement (A1). Les familles naviguent depuis un fournisseur
//    d'accès — Orange, SFR, Free, Bouygues —, pas depuis un centre de données.
//    Deux règles, pour éviter les homonymes :
//    · des numéros de réseau (ASN) pour les hébergeurs qui ont aussi une activité
//      de fournisseur d'accès sous un autre numéro (OVH, IONOS) ;
//    · des noms pour les hébergeurs sans activité grand public.
//    Volontairement ABSENTS : Akamai, Cloudflare et Fastly, qui portent le relais
//    privé d'Apple (iCloud Private Relay) — des humains, en nombre.
export const ASN_HEBERGEURS = new Set([
  16509, 14618,      // Amazon Web Services
  15169, 396982,     // Google, Google Cloud
  8075,              // Microsoft, Azure
  16276,             // OVH (hébergement ; OVH Télécom a un autre numéro)
  24940,             // Hetzner
  14061,             // DigitalOcean
  63949,             // Linode / Akamai Connected Cloud
  12876,             // Scaleway (Online SAS)
  51167,             // Contabo
  31898,             // Oracle Cloud
  20473,             // Vultr (Choopa)
  60781,             // Leaseweb
  45102,             // Alibaba Cloud
  132203,            // Tencent Cloud
  9009,              // M247
  8560,              // IONOS (hébergement)
]);
const NOMS_HEBERGEURS = /hetzner|digitalocean|contabo|vultr|choopa|leaseweb|linode|scaleway|m247|datacamp|alibaba|tencent|oracle cloud|amazon|google cloud|azure|hosting|\bservers?\b|data ?cent(er|re)/i;

export function estHebergeur(cf) {
  if (!cf) return false;
  if (cf.asn && ASN_HEBERGEURS.has(Number(cf.asn))) return true;
  return NOMS_HEBERGEURS.test(String(cf.asOrganization || ''));
}

/** Classe une requête. L'ordre compte : un robot qui s'annonce est « déclaré »
 *  même s'il vient d'un hébergeur — c'est l'information la plus sûre. */
export function classe({ ua, auto, cf, origine }) {
  if (estDeclare(ua)) return { c: DECLARE, motif: null };
  // Le masque de bits dit QUELLE règle a signalé l'automatisation : utile pour
  // repérer une règle qui rangerait des humains parmi les suspects.
  if (auto) return { c: SUSPECT, motif: 'auto:' + auto };
  if (estHebergeur(cf)) {
    const nom = String((cf && cf.asOrganization) || ('AS' + (cf && cf.asn))).slice(0, 40);
    return { c: SUSPECT, motif: 'hebergeur:' + nom };
  }
  if (!origine) return { c: SUSPECT, motif: 'sans-origine' };
  return { c: HUMAIN, motif: null };
}

/** Chemin seul, assaini, puis confronté à la liste du sitemap (C2). Jamais la
 *  chaîne de requête : les liens de partage y portent la situation du visiteur. */
export function chemin(brut) {
  let s = String(brut == null ? '' : brut).split('?')[0].split('#')[0];
  if (s[0] !== '/') s = '/' + s;
  s = s.replace(/[^A-Za-z0-9/_.\-]/g, '').replace(/\/{2,}/g, '/');
  if (s.endsWith('/index.html')) s = s.slice(0, -'index.html'.length);
  return CHEMINS.has(s) ? s : HORS_LISTE;
}

export function domaine(brut) {
  const s = String(brut == null ? '' : brut).toLowerCase()
    .replace(/^www\./, '').replace(/[^a-z0-9.\-]/g, '');
  return s.length > 80 ? s.slice(0, 80) : s;
}

const entetes = (extra) => Object.assign({
  'Access-Control-Allow-Origin': 'https://' + SITE,
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
  'Cache-Control': 'no-store',
}, extra || {});
const vide = () => new Response(null, { status: 204, headers: entetes() });
const json = (o, statut) => new Response(JSON.stringify(o),
  { status: statut || 200, headers: entetes({ 'Content-Type': 'application/json' }) });
const ech = (t) => String(t == null ? '' : t).replace(/[&<>"']/g,
  (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

// ── Enregistrement
async function compte(request, env) {
  const u = new URL(request.url);
  const origine = request.headers.get('Origin');
  // C1. Une requête lancée depuis un autre site ne décrit aucune visite de
  // celui-ci : ignorée, sans trace. Une requête SANS origine n'est pas jetée
  // mais rangée parmi les suspects — aucun navigateur n'en envoie depuis la page.
  if (origine && !ORIGINES.has(origine)) return vide();

  const engagement = u.searchParams.get('t') === 'g';
  const c = chemin(u.searchParams.get('p'));
  const { c: cl, motif } = classe({
    ua: request.headers.get('User-Agent'),
    auto: Math.min(15, Math.max(0, parseInt(u.searchParams.get('a'), 10) || 0)),
    cf: request.cf,
    origine,
  });
  const { jour, heure } = quand(new Date());
  const ecritures = [];

  if (engagement) {
    ecritures.push(env.DB.prepare(
      `INSERT INTO vues (jour, heure, chemin, classe, vues, engages, entrees) VALUES (?, ?, ?, ?, 0, 1, 0)
       ON CONFLICT(jour, heure, chemin, classe) DO UPDATE SET engages = engages + 1`)
      .bind(jour, heure, c, cl));
  } else {
    const entree = u.searchParams.get('e') === '1' ? 1 : 0;
    ecritures.push(env.DB.prepare(
      `INSERT INTO vues (jour, heure, chemin, classe, vues, engages, entrees) VALUES (?, ?, ?, ?, 1, 0, ?)
       ON CONFLICT(jour, heure, chemin, classe)
       DO UPDATE SET vues = vues + 1, entrees = entrees + excluded.entrees`)
      .bind(jour, heure, c, cl, entree));
    // Les tables annexes ne s'écrivent que quand elles portent une information :
    // une vue humaine ordinaire ne coûte qu'une écriture.
    if (motif) ecritures.push(env.DB.prepare(
      `INSERT INTO motifs (jour, motif, vues) VALUES (?, ?, 1)
       ON CONFLICT(jour, motif) DO UPDATE SET vues = vues + 1`).bind(jour, motif));
    const d = domaine(u.searchParams.get('r'));
    if (d && cl === HUMAIN) ecritures.push(env.DB.prepare(
      `INSERT INTO sources (jour, domaine, vues) VALUES (?, ?, 1)
       ON CONFLICT(jour, domaine) DO UPDATE SET vues = vues + 1`).bind(jour, d));
    const pays = (request.cf && request.cf.country) || request.headers.get('CF-IPCountry');
    if (entree && cl === HUMAIN && pays && /^[A-Z]{2}$/.test(pays)) ecritures.push(env.DB.prepare(
      `INSERT INTO pays (jour, code, visites) VALUES (?, ?, 1)
       ON CONFLICT(jour, code) DO UPDATE SET visites = visites + 1`).bind(jour, pays));
  }
  await env.DB.batch(ecritures);
  return vide();
}

// ── Lecture
const PERIODES = {
  jour:    "jour",
  semaine: "strftime('%Y — S%W', jour)",
  mois:    "substr(jour, 1, 7)",
};

async function releve(env, depuis) {
  const q = (sql, ...a) => env.DB.prepare(sql).bind(...a).all().then((r) => r.results || []);
  const par = (k) => q(
    `SELECT ${PERIODES[k]} AS periode,
            SUM(CASE WHEN classe = 0 THEN vues    ELSE 0 END) AS vues,
            SUM(CASE WHEN classe = 0 THEN engages ELSE 0 END) AS engages,
            SUM(CASE WHEN classe = 0 THEN entrees ELSE 0 END) AS entrees,
            SUM(CASE WHEN classe = 1 THEN vues    ELSE 0 END) AS declares,
            SUM(CASE WHEN classe = 2 THEN vues    ELSE 0 END) AS suspects
       FROM vues WHERE jour >= ? GROUP BY periode ORDER BY periode DESC LIMIT 40`, depuis);
  const [jour, semaine, mois, pages, horsListe, motifs, sources, pays, heures] = await Promise.all([
    par('jour'), par('semaine'), par('mois'),
    q(`SELECT chemin, SUM(vues) AS vues, SUM(engages) AS engages, SUM(entrees) AS entrees FROM vues
        WHERE jour >= ? AND classe = 0 AND chemin <> ? GROUP BY chemin ORDER BY vues DESC LIMIT 25`, depuis, HORS_LISTE),
    q(`SELECT classe, SUM(vues) AS vues FROM vues WHERE jour >= ? AND chemin = ? GROUP BY classe`, depuis, HORS_LISTE),
    q(`SELECT motif, SUM(vues) AS vues FROM motifs WHERE jour >= ? GROUP BY motif ORDER BY vues DESC LIMIT 20`, depuis),
    q(`SELECT domaine, SUM(vues) AS vues FROM sources WHERE jour >= ? GROUP BY domaine ORDER BY vues DESC LIMIT 25`, depuis),
    q(`SELECT code, SUM(visites) AS visites FROM pays WHERE jour >= ? GROUP BY code ORDER BY visites DESC LIMIT 25`, depuis),
    q(`SELECT heure, SUM(engages) AS engages FROM vues
        WHERE jour >= ? AND classe = 0 AND heure >= 0 GROUP BY heure ORDER BY heure`, depuis),
  ]);
  const taux = (l) => l.map((x) => Object.assign(x, {
    taux: x.vues ? Math.round(100 * x.engages / x.vues) + ' %' : '—' }));
  return { depuis, jour: taux(jour), semaine: taux(semaine), mois: taux(mois),
           pages: taux(pages), horsListe, motifs, sources, pays, heures };
}

function tableau(titre, lignes, colonnes, note) {
  const n = note ? `<p class="v">${note}</p>` : '';
  if (!lignes.length) return `<h2>${ech(titre)}</h2>${n}<p class="v">Aucune donnée.</p>`;
  return `<h2>${ech(titre)}</h2>${n}<table><thead><tr>${
    colonnes.map((c) => `<th>${ech(c[0])}</th>`).join('')}</tr></thead><tbody>${
    lignes.map((l) => `<tr>${colonnes.map((c) =>
      `<td>${ech(l[c[1]] == null ? '—' : l[c[1]])}</td>`).join('')}</tr>`).join('')
  }</tbody></table>`;
}

const COLS = [['Visites engagées','engages'],['Chargements','vues'],['Taux d’engagement','taux'],
              ['Entrées','entrees'],['Robots déclarés','declares'],['Suspects','suspects']];

function ecran(d) {
  const max = Math.max(1, ...d.heures.map((h) => h.engages));
  const profil = d.heures.length
    ? `<h2>Heures de consultation</h2><div class="h">${Array.from({ length: 24 }, (_, i) => {
        const v = (d.heures.find((x) => x.heure === i) || { engages: 0 }).engages;
        return `<i style="height:${Math.round((v / max) * 100)}%" title="${i} h : ${v}"></i>`;
      }).join('')}</div><p class="v">Visites engagées d’humains, de 0 h à 23 h, heure de Paris.</p>` : '';
  const hl = d.horsListe.reduce((a, x) => a + x.vues, 0);
  return `<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Audience — Trouver mon EHPAD</title>
<style>
:root{color-scheme:light dark}
body{margin:0;padding:1.5rem;font:15px/1.5 system-ui,sans-serif;max-width:66rem;margin-inline:auto}
h1{font-size:1.5rem;margin:0 0 .25rem}h2{font-size:1rem;margin:2rem 0 .5rem}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:.35rem .6rem;border-bottom:1px solid #8883}
td+td,th+th{text-align:right}
.v{color:#8a8a8a;font-size:.85rem;margin:.2rem 0 .5rem}
.h{display:flex;align-items:flex-end;gap:2px;height:90px;margin-top:.5rem}
.h i{flex:1;background:#2548FF;min-height:1px;border-radius:2px 2px 0 0}
</style></head><body>
<h1>Audience</h1><p class="v">Depuis le ${ech(d.depuis)}. Heure de Paris.</p>
<p class="v"><b>Visite engagée</b> : quelqu’un a défilé, cliqué, touché l’écran ou tapé au clavier,
ou l’onglet est resté visible 10 secondes. <b>Chargement</b> : la page s’est affichée. L’écart entre
les deux mesure les passages éclairs et le trafic fantôme. Robots déclarés et suspects ne sont
jamais mêlés aux humains.</p>
${tableau('Par jour', d.jour, [['Jour','periode'], ...COLS])}
${tableau('Par semaine', d.semaine, [['Semaine','periode'], ...COLS])}
${tableau('Par mois', d.mois, [['Mois','periode'], ...COLS])}
${profil}
${tableau('Pages les plus vues (humains)', d.pages, [['Page','chemin'],['Visites engagées','engages'],['Chargements','vues'],['Taux','taux'],['Entrées','entrees']])}
${tableau('Pourquoi des vues sont suspectes', d.motifs, [['Motif','motif'],['Vues','vues']],
  'À surveiller : si un réseau grand public apparaît ici, la règle range des humains parmi les suspects.')}
<h2>Chemins hors sitemap</h2><p class="v">${hl} chargement(s) sur des adresses absentes du sitemap —
pages d’erreur, adresses fabriquées, ou page ajoutée au site sans relancer build/chemins_mesure.py.</p>
${tableau('Sites référents (humains)', d.sources, [['Domaine','domaine'],['Vues','vues']])}
${tableau('Pays (entrées humaines)', d.pays, [['Pays','code'],['Visites','visites']])}
<p class="v" style="margin-top:2rem">Un visiteur qui bloque les scripts n’est pas compté, et un robot qui
pilote un vrai navigateur depuis une connexion résidentielle peut passer pour un humain : aucun
relevé de ce type n’est exhaustif.</p>
</body></html>`;
}

export default {
  async fetch(request, env) {
    const u = new URL(request.url);
    if (request.method === 'OPTIONS') return vide();

    if (u.pathname === '/v') {
      // Le relevé ne doit jamais faire échouer une page : toute erreur est avalée.
      try { return await compte(request, env); } catch (e) { return vide(); }
    }

    if (u.pathname === '/mesure' || u.pathname === '/mesure.json') {
      if (!env.CLE_MESURE || u.searchParams.get('cle') !== env.CLE_MESURE) return json({ erreur: 'interdit' }, 403);
      const n = Math.min(1095, Math.max(1, Number(u.searchParams.get('jours')) || 90));
      const depuis = quand(new Date(Date.now() - n * 86400000)).jour;
      const r = await releve(env, depuis);
      if (u.pathname === '/mesure.json') return json(r);
      return new Response(ecran(r), { headers: entetes({
        'Content-Type': 'text/html; charset=utf-8', 'X-Robots-Tag': 'noindex, nofollow' }) });
    }
    return json({ erreur: 'inconnu' }, 404);
  },

  /** Au-delà de 400 jours, les 24 lignes horaires d'une page deviennent une
   *  seule ligne (heure = -1) : le total du jour est conservé, le détail horaire perdu. */
  async scheduled(evt, env) {
    const seuil = quand(new Date(Date.now() - 400 * 86400000)).jour;
    await env.DB.prepare(
      `INSERT INTO vues (jour, heure, chemin, classe, vues, engages, entrees)
       SELECT jour, -1, chemin, classe, SUM(vues), SUM(engages), SUM(entrees) FROM vues
        WHERE jour < ? AND heure >= 0 GROUP BY jour, chemin, classe
       ON CONFLICT(jour, heure, chemin, classe) DO UPDATE SET
         vues = vues + excluded.vues, engages = engages + excluded.engages, entrees = entrees + excluded.entrees`)
      .bind(seuil).run();
    await env.DB.prepare('DELETE FROM vues WHERE jour < ? AND heure >= 0').bind(seuil).run();
  },
};
