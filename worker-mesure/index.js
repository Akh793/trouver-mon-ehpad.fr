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
export const HUMAIN = 0, DECLARE = 1, SUSPECT = 2, PROPRIO = 3;
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
export function classe({ ua, auto, cf, origine, proprio }) {
  if (estDeclare(ua)) return { c: DECLARE, motif: null };
  // Le propriétaire du site, marqué dans son propre navigateur par le lien
  // #ne-pas-me-compter : rangé à part, jamais mêlé aux visiteurs. Exige une
  // origine, pour qu'un appel fabriqué à la main ne puisse pas s'y glisser.
  if (proprio && origine) return { c: PROPRIO, motif: null };
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
    proprio: u.searchParams.get('m') === '1',
  });
  const { jour, heure } = quand(new Date());
  // Étape du parcours sur l'accueil : une ligne par (jour, étape, appareil, classe).
  // Toute autre page, ou une étape inconnue, est ignorée sans trace.
  if (u.searchParams.get('t') === 'e') {
    const k = u.searchParams.get('k');
    if (c !== '/' || !ETAPES.some((x) => x[0] === k)) return vide();
    await env.DB.batch([env.DB.prepare(
      `INSERT INTO etapes (jour, etape, appareil, classe, n) VALUES (?, ?, ?, ?, 1)
       ON CONFLICT(jour, etape, appareil, classe) DO UPDATE SET n = n + 1`)
      .bind(jour, k, u.searchParams.get('d') === '1' ? 1 : 0, cl)]);
    return vide();
  }
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

/** Série quotidienne continue, du premier jour enregistré à aujourd'hui :
 *  un jour sans ligne vaut 0 — sinon la courbe relierait deux jours éloignés
 *  et masquerait les creux. Dates 'AAAA-MM-JJ' (heure de Paris), calcul en UTC
 *  sur la date seule : aucun décalage d'heure d'été possible. */
/** Profil horaire (0 h à 23 h) pour chaque période du graphique, à partir d'une
 *  seule lecture de la base : [[engagées, chargements] × 24] par période. */
export const PERIODES_H = ['30', '90', '365', 'tout'];
export function profilHeures(lignes) {
  const out = {};
  for (const f of PERIODES_H) out[f] = Array.from({ length: 24 }, () => [0, 0]);
  for (const l of lignes) {
    const h = Number(l.heure); if (!(h >= 0 && h <= 23)) continue;
    const v = { '30': [l.e30, l.c30], '90': [l.e90, l.c90], '365': [l.e365, l.c365], tout: [l.et, l.ct] };
    for (const f of PERIODES_H) out[f][h] = [Number(v[f][0]) || 0, Number(v[f][1]) || 0];
  }
  return out;
}

/** Étapes du parcours sur l'accueil, dans l'ordre, et leur part des arrivées. */
export const ETAPES = [['a', 'Arrivée sur l’accueil'], ['cp', 'Résultats affichés (code postal)'],
                       ['r', 'Budget calculé (ressources)'], ['f', 'Fiche d’un établissement ouverte']];
export function parcours(lignes) {
  const v = (k, d) => lignes.filter((l) => l.etape === k && Number(l.appareil) === d)
    .reduce((a, l) => a + (Number(l.n) || 0), 0);
  const base = v('a', 0) + v('a', 1);
  return ETAPES.map(([k, lib]) => {
    const tactile = v(k, 1), souris = v(k, 0), total = tactile + souris;
    return { etape: lib, tactile, souris, total,
             part: base ? Math.round(100 * total / base) + ' %' : '—' };
  });
}

export function serieJours(lignes, premier, auj) {
  const par = new Map(lignes.map((l) => [l.jour, l]));
  const out = [];
  if (!premier || premier > auj) premier = auj;
  for (let t = Date.parse(premier + 'T00:00:00Z'), fin = Date.parse(auj + 'T00:00:00Z'); t <= fin; t += 86400000) {
    const j = new Date(t).toISOString().slice(0, 10), l = par.get(j);
    out.push([j, l ? Number(l.e) || 0 : 0, l ? Number(l.c) || 0 : 0]);
  }
  return out;
}

async function releve(env, depuis) {
  const q = (sql, ...a) => env.DB.prepare(sql).bind(...a).all().then((r) => r.results || []);
  const par = (k) => q(
    `SELECT ${PERIODES[k]} AS periode,
            SUM(CASE WHEN classe = 0 THEN vues    ELSE 0 END) AS vues,
            SUM(CASE WHEN classe = 0 THEN engages ELSE 0 END) AS engages,
            SUM(CASE WHEN classe = 0 THEN entrees ELSE 0 END) AS entrees,
            SUM(CASE WHEN classe = 1 THEN vues    ELSE 0 END) AS declares,
            SUM(CASE WHEN classe = 2 THEN vues    ELSE 0 END) AS suspects,
            SUM(CASE WHEN classe = 3 THEN vues    ELSE 0 END) AS vous
       FROM vues WHERE jour >= ? GROUP BY periode ORDER BY periode DESC LIMIT 40`, depuis);
  // Graphique : sa propre lecture, sans la limite de 40 lignes des tableaux, sur 3 ans au plus.
  const il = (k) => quand(new Date(Date.now() - k * 86400000)).jour;   // « il y a k jours », heure de Paris
  const auj = quand(new Date()).jour;
  const borne = il(1095);
  const [jour, semaine, mois, pages, horsListe, motifs, sources, pays, heures, gj, gp, et] = await Promise.all([
    par('jour'), par('semaine'), par('mois'),
    q(`SELECT chemin, SUM(vues) AS vues, SUM(engages) AS engages, SUM(entrees) AS entrees FROM vues
        WHERE jour >= ? AND classe = 0 AND chemin <> ? GROUP BY chemin ORDER BY vues DESC LIMIT 25`, depuis, HORS_LISTE),
    q(`SELECT classe, SUM(vues) AS vues FROM vues WHERE jour >= ? AND chemin = ? GROUP BY classe`, depuis, HORS_LISTE),
    q(`SELECT motif, SUM(vues) AS vues FROM motifs WHERE jour >= ? GROUP BY motif ORDER BY vues DESC LIMIT 20`, depuis),
    q(`SELECT domaine, SUM(vues) AS vues FROM sources WHERE jour >= ? GROUP BY domaine ORDER BY vues DESC LIMIT 25`, depuis),
    q(`SELECT code, SUM(visites) AS visites FROM pays WHERE jour >= ? GROUP BY code ORDER BY visites DESC LIMIT 25`, depuis),
    // Heures : les 4 périodes du graphique en une seule lecture. Le détail horaire
    // n'existe que sur 400 jours (au-delà, la tâche de nuit le replie en heure = -1).
    q(`SELECT heure,
              SUM(CASE WHEN jour >= ? THEN engages ELSE 0 END) AS e30,  SUM(CASE WHEN jour >= ? THEN vues ELSE 0 END) AS c30,
              SUM(CASE WHEN jour >= ? THEN engages ELSE 0 END) AS e90,  SUM(CASE WHEN jour >= ? THEN vues ELSE 0 END) AS c90,
              SUM(CASE WHEN jour >= ? THEN engages ELSE 0 END) AS e365, SUM(CASE WHEN jour >= ? THEN vues ELSE 0 END) AS c365,
              SUM(engages) AS et, SUM(vues) AS ct
         FROM vues WHERE jour >= ? AND classe = 0 AND heure >= 0 GROUP BY heure ORDER BY heure`,
      il(29), il(29), il(89), il(89), il(364), il(364), il(400)),   // pas plus loin : moins de lignes lues
    q(`SELECT jour, SUM(CASE WHEN classe = 0 THEN engages ELSE 0 END) AS e,
              SUM(CASE WHEN classe = 0 THEN vues    ELSE 0 END) AS c
         FROM vues WHERE jour >= ? GROUP BY jour ORDER BY jour`, borne),
    q(`SELECT MIN(jour) AS premier FROM vues WHERE jour >= ?`, borne),
    // Avant la création de la table (schema.sql relancé), le tableau reste simplement vide.
    Promise.resolve().then(() => q(
      `SELECT etape, appareil, SUM(n) AS n FROM etapes WHERE jour >= ? AND classe = 0 GROUP BY etape, appareil`, depuis))
      .catch(() => []),
  ]);
  const taux = (l) => l.map((x) => Object.assign(x, {
    taux: x.vues ? Math.round(100 * x.engages / x.vues) + ' %' : '—' }));
  return { depuis, jour: taux(jour), semaine: taux(semaine), mois: taux(mois),
           pages: taux(pages), horsListe, motifs, sources, pays, heures: profilHeures(heures),
           parcours: parcours(et),
           graphe: { auj, jours: serieJours(gj, gp[0] && gp[0].premier, auj) } };
}

function tableau(titre, lignes, colonnes, note) {
  const n = note ? `<p class="v">${note}</p>` : '';
  if (!lignes.length) return `<h2>${ech(titre)}</h2>${n}<p class="v">Aucune donnée.</p>`;
  return `<h2>${ech(titre)}</h2>${n}<div class="tab"><table><thead><tr>${
    colonnes.map((c) => `<th>${ech(c[0])}</th>`).join('')}</tr></thead><tbody>${
    lignes.map((l) => `<tr>${colonnes.map((c) =>
      `<td>${ech(l[c[1]] == null ? '—' : l[c[1]])}</td>`).join('')}</tr>`).join('')
  }</tbody></table></div>`;
}

const COLS = [['Visites engagées','engages'],['Chargements','vues'],['Taux d’engagement','taux'],
              ['Entrées','entrees'],['Robots déclarés','declares'],['Suspects','suspects'],['Vous','vous']];

function ecran(d) {
  const hl = d.horsListe.reduce((a, x) => a + x.vues, 0);
  return `<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Audience — Trouver mon EHPAD</title>
<script>try{var t=localStorage.getItem('tme_theme_mesure');if(t==='dark'||t==='light')document.documentElement.setAttribute('data-theme',t)}catch(e){}</script>
<style>
:root{--bg:#fff;--fg:#0f172a;--mut:#64748b;--ln:#e2e8f0;--bl:#2548FF;--piste:#475569;--pouce:#fff;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0d1117;--fg:#e8edf5;--mut:#a3aec0;--ln:#263041;--bl:#8ba4ff;--piste:#8ba4ff;--pouce:#0d1117;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0d1117;--fg:#e8edf5;--mut:#a3aec0;--ln:#263041;--bl:#8ba4ff;--piste:#8ba4ff;--pouce:#0d1117;color-scheme:dark}
html{background:var(--bg)}
body{margin:0;padding:1.5rem;font:15px/1.5 system-ui,sans-serif;max-width:66rem;margin-inline:auto;background:var(--bg);color:var(--fg)}
.tete{display:flex;align-items:center;justify-content:space-between;gap:1rem;flex-wrap:wrap}
.sw{display:inline-flex;align-items:center;gap:.5rem;height:34px;padding:0 .3rem 0 .75rem;border-radius:999px;cursor:pointer;
  border:1.5px solid var(--ln);background:transparent;color:var(--fg);font:600 .8rem/1 system-ui,sans-serif}
.sw:hover,.sw:focus-visible{border-color:var(--bl)}
.sw i{position:relative;width:36px;height:20px;border-radius:999px;background:var(--piste)}
.sw i::after{content:"";position:absolute;top:2px;left:2px;width:16px;height:16px;border-radius:50%;background:var(--pouce);
  box-shadow:0 1px 3px rgba(0,0,0,.3);transition:transform .2s}
.sw[aria-checked="true"] i::after{transform:translateX(16px)}
@media (prefers-reduced-motion:reduce){.sw i::after{transition:none}}
h1{font-size:1.5rem;margin:0 0 .25rem}h2{font-size:1rem;margin:2rem 0 .5rem}
.tab{overflow-x:auto;-webkit-overflow-scrolling:touch}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}
th{white-space:nowrap}
th,td{text-align:left;padding:.35rem .6rem;border-bottom:1px solid var(--ln)}
td+td,th+th{text-align:right}
.v{color:var(--mut);font-size:.85rem;margin:.2rem 0 .5rem}
:root{--ligne:#64748b;--moy:#0f172a}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--ligne:#8b97ab;--moy:#e8edf5}}
:root[data-theme="dark"]{--ligne:#8b97ab;--moy:#e8edf5}
.g-barre{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:.5rem 1rem;margin:.25rem 0 .5rem}
.leg{display:flex;flex-wrap:wrap;gap:.3rem 1rem;font-size:.85rem;color:var(--mut)}
.leg span{display:inline-flex;align-items:center;gap:.4rem}
.leg i{display:inline-block;width:12px;height:12px;border-radius:3px;background:var(--bl)}
.leg i.l{height:2px;border-radius:1px;background:var(--ligne)}
.leg i.m{height:2px;border-radius:1px;background:var(--moy)}
.fen{display:inline-flex;border:1.5px solid var(--ln);border-radius:999px;padding:2px}
.fen button{border:0;background:transparent;color:var(--mut);font:600 .78rem/1 system-ui,sans-serif;padding:.4rem .7rem;border-radius:999px;cursor:pointer}
.fen button[aria-pressed="true"]{background:var(--bl);color:var(--bg)}
.fen button:focus-visible{outline:2px solid var(--bl);outline-offset:1px}
.gbox{position:relative;width:100%}
.gbox svg{display:block;width:100%;height:240px;overflow:visible}
.gbox svg:focus-visible{outline:2px solid var(--bl);outline-offset:4px;border-radius:4px}
.gbox .gr{stroke:var(--ln);stroke-width:1}
.gbox .ax{fill:var(--mut);font:11px system-ui,sans-serif;font-variant-numeric:tabular-nums}
.gbox .b{fill:var(--bl)}
.gbox .b.auj{opacity:.45}
.gbox .lc{fill:none;stroke:var(--ligne);stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
.gbox .pc{fill:var(--ligne);stroke:var(--bg);stroke-width:2}
.gbox .lm{fill:none;stroke:var(--moy);stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
.gbox .x{stroke:var(--mut);stroke-width:1;opacity:.6}
.gtip{position:absolute;pointer-events:none;background:var(--bg);color:var(--fg);border:1px solid var(--ln);border-radius:8px;
  padding:.45rem .6rem;font-size:.8rem;line-height:1.4;box-shadow:0 6px 20px rgba(0,0,0,.18);white-space:nowrap;display:none;z-index:2}
.gtip b{font-weight:600}.gtip .t{color:var(--mut)}
</style></head><body>
<div class="tete"><h1>Audience</h1>
<button type="button" class="sw" id="sw" role="switch" aria-checked="false" aria-label="Mode sombre">Sombre<i aria-hidden="true"></i></button></div><p class="v">Depuis le ${ech(d.depuis)}. Heure de Paris.</p>
<p class="v"><b>Visite engagée</b> : quelqu’un a défilé, cliqué, touché l’écran ou tapé au clavier,
ou l’onglet est resté visible 10 secondes. <b>Chargement</b> : la page s’est affichée. L’écart entre
les deux mesure les passages éclairs et le trafic fantôme. Robots déclarés et suspects ne sont
jamais mêlés aux humains. <b>Vous</b> : vos propres chargements, depuis un navigateur marqué par le lien
#ne-pas-me-compter.</p>
<h2>Visites par jour</h2>
<div class="g-barre"><div class="leg" id="gleg"><span><i></i>Visites engagées (humains)</span><span><i class="l"></i><b class="lcg" style="font-weight:inherit">Chargements (humains)</b></span></div>
<div class="fen" id="fenj" role="group" aria-label="Période du graphique"><button type="button" data-f="30" aria-pressed="false">30 j</button><button type="button" data-f="90" aria-pressed="false">90 j</button><button type="button" data-f="365" aria-pressed="false">1 an</button><button type="button" data-f="tout" aria-pressed="true">Tout</button></div></div>
<div id="graphe" class="gbox"><div id="gtip" class="gtip" role="status" aria-live="polite"></div></div>
<p class="v">Relu dans la base à chaque ouverture : l’historique s’ajoute seul. Jours sans visite comptés à 0 ; journée en cours en barre pâle. Survol, toucher ou flèches du clavier pour les chiffres exacts.</p>
<script type="application/json" id="gdata">${JSON.stringify(d.graphe || { auj: '', jours: [] }).replace(/</g, '\\u003c')}</script>
${tableau('Par jour', d.jour, [['Jour','periode'], ...COLS])}
${tableau('Par semaine', d.semaine, [['Semaine','periode'], ...COLS])}
${tableau('Par mois', d.mois, [['Mois','periode'], ...COLS])}
<h2>Heures de consultation</h2>
<div class="g-barre"><div class="leg"><span><i></i>Visites engagées (humains)</span><span><i class="l"></i>Chargements (humains)</span></div>
<div class="fen" id="fenh" role="group" aria-label="Période du graphique"><button type="button" data-f="30" aria-pressed="false">30 j</button><button type="button" data-f="90" aria-pressed="false">90 j</button><button type="button" data-f="365" aria-pressed="false">1 an</button><button type="button" data-f="tout" aria-pressed="true">Tout</button></div></div>
<div id="gheures" class="gbox"><div id="htip" class="gtip" role="status" aria-live="polite"></div></div>
<p class="v">Cumul par tranche horaire, heure de Paris, relu à chaque ouverture. « Tout » couvre au plus les 400 derniers jours : au-delà, la tâche de nuit ne garde que le total du jour.</p>
<script type="application/json" id="hdata">${JSON.stringify(d.heures || {}).replace(/</g, '\\u003c')}</script>
${tableau('Parcours sur l’accueil (humains)', d.parcours || [],
  [['Étape','etape'],['Écran tactile','tactile'],['Souris','souris'],['Total','total'],['Part des arrivées','part']],
  'Chargements de l’accueil où l’étape a été atteinte au moins une fois, sur la période. Mesuré depuis le 29/09/2026. Tactile = téléphone ou tablette.')}
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
<script>(function(){
var NS='http://www.w3.org/2000/svg',MOIS=['janv.','févr.','mars','avr.','mai','juin','juil.','août','sept.','oct.','nov.','déc.'];
function dl(j){var p=j.split('-');return (+p[2])+' '+MOIS[+p[1]-1]+' '+p[0];}
function dc(j){var p=j.split('-');return p[2]+'/'+p[1];}
function nb(v){return Math.round(v).toLocaleString('fr-FR');}
function pas(m){var r=m/4,e=Math.pow(10,Math.floor(Math.log10(r)));r/=e;return Math.max(1,(r<=1?1:r<=2?2:r<=5?5:10)*e);}
function el(n,a,t){var e=document.createElementNS(NS,n);for(var k in a)e.setAttribute(k,a[k]);if(t!=null)e.textContent=t;return e;}
function donnee(id){try{return JSON.parse(document.getElementById(id).textContent);}catch(e){return null;}}
/* Moteur commun. o.pts : [[engagées, chargements]…] ; o.lisse : moyennes 7 j ; o.pale : index en barre pâle ;
   o.ticks : [[index, texte]…] ; o.titre(i) : en-tête de l'infobulle ; o.resume : texte pour lecteur d'écran. */
function dessine(box,tip,o){
 var d=o.pts,n=d.length,old=box.querySelector('svg');if(old)old.remove();tip.style.display='none';if(!n)return;
 var W=Math.max(260,box.clientWidth),H=o.haut||240,ml=40,mr=10,mt=10,mb=26,pw=W-ml-mr,ph=H-mt-mb,sl=pw/n,cur=-1;
 var max=0,tot=0;d.forEach(function(x){if(x[0]>max)max=x[0];if(x[1]>max)max=x[1];tot+=x[0];});
 var st=pas(Math.max(max,1)),ym=st*Math.max(1,Math.ceil(max/st));
 var y=function(v){return mt+ph-v/ym*ph;},cx=function(i){return ml+(i+.5)*sl;};
 var svg=el('svg',{viewBox:'0 0 '+W+' '+H,role:'img',tabindex:'0','aria-label':o.resume});
 svg.style.height=H+'px';
 for(var t=0;t<=ym+1e-9;t+=st){svg.appendChild(el('line',{'class':'gr',x1:ml,x2:W-mr,y1:y(t),y2:y(t)}));
  svg.appendChild(el('text',{'class':'ax',x:ml-6,y:y(t)+4,'text-anchor':'end'},nb(t)));}
 var bw=Math.min(24,Math.max(1,sl-2));
 d.forEach(function(x,i){if(!x[0])return;var h=ph*x[0]/ym,x0=cx(i)-bw/2,y0=mt+ph,r=Math.min(4,bw/2,h),
  pa='M'+x0+','+y0+'V'+(y0-h+r)+'Q'+x0+','+(y0-h)+' '+(x0+r)+','+(y0-h)+'H'+(x0+bw-r)+'Q'+(x0+bw)+','+(y0-h)+' '+(x0+bw)+','+(y0-h+r)+'V'+y0+'Z';
  svg.appendChild(el('path',{'class':'b'+(i===o.pale?' auj':''),d:pa}));});
 function mg(c,i){var s=0,k=Math.max(0,i-6);for(var j=k;j<=i;j++)s+=d[j][c];return s/(i-k+1);}
 if(n===1)svg.appendChild(el('circle',{'class':'pc',cx:cx(0),cy:y(d[0][1]),r:4}));
 else svg.appendChild(el('polyline',{'class':'lc',points:d.map(function(x,i){return cx(i)+','+y(o.lisse?mg(1,i):x[1]);}).join(' ')}));
 if(o.lisse)svg.appendChild(el('polyline',{'class':'lm',points:d.map(function(x,i){return cx(i)+','+y(mg(0,i));}).join(' ')}));
 var last=-1e9;o.ticks.slice().sort(function(a,b){return a[0]-b[0];}).forEach(function(l){var x=cx(l[0]);if(x-last<46)return;last=x;
  svg.appendChild(el('text',{'class':'ax',x:x,y:H-8,'text-anchor':'middle'},l[1]));});
 var cr=el('line',{'class':'x',y1:mt,y2:mt+ph,x1:0,x2:0,visibility:'hidden'});svg.appendChild(cr);
 var zone=el('rect',{x:ml,y:mt,width:pw,height:ph,fill:'transparent'});svg.appendChild(zone);
 function montre(i){if(i<0||i>=n){cache();return;}cur=i;var x=d[i],xx=cx(i);cr.setAttribute('x1',xx);cr.setAttribute('x2',xx);cr.setAttribute('visibility','visible');
  tip.innerHTML=o.titre(i)+'<br>Visites engagées : <b>'+nb(x[0])+'</b>'+(o.part&&tot?' <span class="t">('+Math.round(100*x[0]/tot)+' %)</span>':'')+'<br>Chargements : <b>'+nb(x[1])+'</b>';
  tip.style.display='block';var tw=tip.offsetWidth,sc=box.clientWidth/W,px=xx*sc+12;if(px+tw>box.clientWidth)px=xx*sc-tw-12;
  tip.style.left=Math.max(0,px)+'px';tip.style.top='8px';}
 function cache(){cr.setAttribute('visibility','hidden');tip.style.display='none';}
 function idx(ev){var r=svg.getBoundingClientRect(),x=(ev.clientX-r.left)*W/r.width;return Math.floor((x-ml)/sl);}
 zone.addEventListener('pointermove',function(ev){montre(idx(ev));});
 zone.addEventListener('pointerdown',function(ev){montre(idx(ev));});
 svg.addEventListener('pointerleave',cache);svg.addEventListener('blur',cache);
 svg.addEventListener('keydown',function(ev){var i=cur<0?n-1:cur;
  if(ev.key==='ArrowLeft')i=Math.max(0,i-1);else if(ev.key==='ArrowRight')i=Math.min(n-1,i+1);
  else if(ev.key==='Home')i=0;else if(ev.key==='End')i=n-1;else if(ev.key==='Escape'){cache();return;}else return;
  ev.preventDefault();montre(i);});
 box.insertBefore(svg,tip);
 return pw;}
function periode(id,defaut,rafraichit){var f=defaut;document.querySelectorAll('#'+id+' button').forEach(function(b){b.addEventListener('click',function(){
 f=b.dataset.f;document.querySelectorAll('#'+id+' button').forEach(function(o){o.setAttribute('aria-pressed',String(o===b));});rafraichit();});});
 return function(){return f;};}
function suit(box,fn){var lw=0;function r(){var w=box.clientWidth;if(w!==lw){lw=w;fn();}}
 if(window.ResizeObserver)new ResizeObserver(r).observe(box);else window.addEventListener('resize',r);r();}
var NOMS={'30':'sur les 30 derniers jours','90':'sur les 90 derniers jours','365':'sur la dernière année','tout':'sur tout l’historique horaire'};

/* ── Visites par jour */
var D=donnee('gdata')||{jours:[]},J=D.jours||[],gbox=document.getElementById('graphe'),gtip=document.getElementById('gtip'),leg=document.getElementById('gleg');
var fj=periode('fenj','tout',jours);
function jours(){
 var f=fj(),d=f==='tout'?J:J.slice(-(+f)),n=d.length,moy=n>120,lm=leg.querySelector('.mo'),lc=leg.querySelector('.lcg');
 lc.textContent=moy?'Chargements (moyenne 7 j)':'Chargements (humains)';
 if(moy&&!lm){lm=document.createElement('span');lm.className='mo';lm.innerHTML='<i class="m"></i>Visites engagées (moyenne 7 j)';leg.appendChild(lm);}
 if(!moy&&lm)lm.remove();
 if(!n)return;
 var tot=0,im=0;d.forEach(function(x,i){tot+=x[1];if(x[1]>d[im][1])im=i;});
 var w=Math.max(260,gbox.clientWidth)-50,ticks=[];
 if(n<=120){var k=Math.max(1,Math.ceil(n/Math.max(1,Math.floor(w/52))));for(var i=n-1;i>=0;i-=k)ticks.push([i,dc(d[i][0])]);}
 else{for(var i=0;i<n;i++)if(d[i][0].slice(8)==='01')ticks.push([i,MOIS[+d[i][0].slice(5,7)-1]+' '+d[i][0].slice(2,4)]);}
 dessine(gbox,gtip,{pts:d.map(function(x){return [x[1],x[2]];}),lisse:moy,pale:d[n-1][0]===D.auj?n-1:-1,ticks:ticks,
  titre:function(i){return '<b>'+dl(d[i][0])+'</b>'+(d[i][0]===D.auj?' <span class="t">(en cours)</span>':'');},
  resume:'Visites engagées par jour, du '+dl(d[0][0])+' au '+dl(d[n-1][0])+' : '+nb(tot)+' au total, maximum '+nb(d[im][1])+' le '+dl(d[im][0])+'. Le tableau « Par jour » donne le détail.'});}
suit(gbox,jours);

/* ── Heures de consultation */
var HP=donnee('hdata')||{},hbox=document.getElementById('gheures'),htip=document.getElementById('htip');
var fh=periode('fenh','tout',heures);
function heures(){
 var f=fh(),d=HP[f]||[];if(d.length!==24){d=[];for(var i=0;i<24;i++)d.push([0,0]);}
 var tot=0,im=0;d.forEach(function(x,i){tot+=x[0];if(x[0]>d[im][0])im=i;});
 var w=Math.max(260,hbox.clientWidth)-50,k=[1,2,3,4,6].filter(function(k){return w/24*k>=46;})[0]||6,ticks=[];
 for(var i=0;i<24;i+=k)ticks.push([i,i+' h']);
 dessine(hbox,htip,{pts:d,lisse:false,pale:-1,ticks:ticks,haut:220,part:true,
  titre:function(i){return '<b>'+i+' h – '+(i+1)+' h</b>';},
  resume:'Visites engagées par heure de la journée, heure de Paris, '+NOMS[f]+' : '+(tot?'pic entre '+im+' h et '+(im+1)+' h avec '+nb(d[im][0])+' visites sur '+nb(tot)+'.':'aucune visite engagée.')});}
suit(hbox,heures);
})();</script>
<script>(function(){var r=document.documentElement,b=document.getElementById('sw'),
mq=matchMedia('(prefers-color-scheme:dark)');
function sombre(){var t=r.getAttribute('data-theme');return t?t==='dark':mq.matches;}
function maj(){b.setAttribute('aria-checked',String(sombre()));}
b.addEventListener('click',function(){var t=sombre()?'light':'dark';r.setAttribute('data-theme',t);
 try{localStorage.setItem('tme_theme_mesure',t)}catch(e){}maj();});
if(mq.addEventListener)mq.addEventListener('change',maj);maj();})();</script>
</body></html>`;
}

export default {
  async fetch(request, env) {
    const u = new URL(request.url);
    if (request.method === 'OPTIONS') return vide();

    if (u.pathname === '/v') {
      // Le relevé ne doit jamais faire échouer une page : toute erreur est avalée.
      try { return await compte(request, env); }
      catch (e) { console.error('relevé non enregistré :', e && e.message); return vide(); }   // visible par « wrangler tail »
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
