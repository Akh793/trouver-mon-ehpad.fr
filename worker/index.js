/**
 * Point de réception des retours de trouver-mon-ehpad.fr
 *
 * Le site est statique : il ne peut rien recevoir. Ce Worker reçoit les messages
 * et les publie immédiatement ; l'éditeur en retire ce qui doit l'être.
 *
 * C'est le régime de l'hébergeur au sens de la LCEN : la responsabilité n'est
 * engagée qu'à défaut de retrait prompt après signalement. D'où deux exigences,
 * sans lesquelles ce régime ne tient pas : un moyen de signaler visible sur la
 * page publique, et un écran de retrait immédiatement utilisable.
 *
 * Déploiement : voir worker/LISEZMOI.md
 */

const ORIGINE = 'https://trouver-mon-ehpad.fr';
const MAX_MESSAGE = 1500;
const MAX_NOM = 40;
const DELAI_MINI_MS = 3000;      // un formulaire rempli en moins de 3 s est un robot
const PAR_HEURE = 3;             // messages acceptés depuis une même adresse

const entetes = (extra) => ({
  'Access-Control-Allow-Origin': ORIGINE,
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Content-Type': 'application/json; charset=utf-8',
  'Cache-Control': 'no-store',
  ...extra,
});

const repond = (obj, statut = 200) =>
  new Response(JSON.stringify(obj), { status: statut, headers: entetes() });

/** Empreinte non réversible de l'adresse IP.
    Elle sert uniquement à limiter le débit. Conserver l'adresse en clair
    n'apporterait rien au service et ferait entrer une donnée identifiante
    dans la base. */
async function empreinte(ip, sel) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(sel + '|' + ip));
  return [...new Uint8Array(buf)].slice(0, 12).map((b) => b.toString(16).padStart(2, '0')).join('');
}

/** Retire les caractères de contrôle et neutralise les chevrons.
    L'affichage échappe déjà, mais une donnée propre en base vaut mieux
    qu'une donnée nettoyée à chaque lecture. */
const nettoie = (t, max) =>
  String(t == null ? '' : t)
    .replace(/[\u0000-\u001F\u007F]/g, '')
    .replace(/</g, '‹').replace(/>/g, '›')
    .trim().slice(0, max);

/** Échappement HTML. Le contenu vient de visiteurs anonymes : il ne doit jamais
    être interprété comme du balisage, ici pas plus qu'ailleurs. */
const ech = (t) => String(t == null ? '' : t)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;').replace(/'/g, '&#39;');

/** Écran de modération, sans dépendance ni mise en forme superflue :
    il sert à lire, publier, refuser ou effacer. */
function pageAdmin(lignes, cle) {
  const enLigne = lignes.filter((l) => l.etat === 'publie').length;
  const bloc = (l) => `<article class="m ${ech(l.etat)}">
      <p class="h"><b>${l.nom ? ech(l.nom) : 'Sans nom'}</b> · ${ech(l.recu_le)} · ${ech(l.etat)}</p>
      <p class="t">${ech(l.message)}</p>
      <p class="a">
        ${l.etat === 'publie'
          ? `<button data-id="${l.id}" data-etat="refuse">Retirer du site</button>`
          : `<button data-id="${l.id}" data-etat="publie">Remettre en ligne</button>`}
        <button data-id="${l.id}" data-sup="1" class="sup">Effacer définitivement</button>
      </p></article>`;
  return `<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex, nofollow"><title>Modération des retours</title>
<style>
body{font:15px/1.5 system-ui,sans-serif;max-width:46rem;margin:2rem auto;padding:0 1rem;color:#0f172a}
h1{font-size:1.3rem} .att{background:#fff7ed;border:1px solid #fdba74;padding:.6rem .9rem;border-radius:.5rem}
.m{border:1px solid #e2e8f0;border-left:4px solid #94a3b8;border-radius:.5rem;padding:.8rem 1rem;margin:.8rem 0}
.m.attente{border-left-color:#e08a00;background:#fffbf5}
.m.publie{border-left-color:#0f8a5f} .m.refuse{border-left-color:#d1344b;opacity:.6}
.h{font-size:.8rem;color:#64748b;margin:0 0 .4rem} .t{margin:0 0 .6rem;white-space:pre-wrap}
.a{margin:0;display:flex;gap:.4rem;flex-wrap:wrap}
button{font:inherit;font-size:.8rem;padding:.3rem .7rem;border:1px solid #cbd5e1;background:#fff;border-radius:999px;cursor:pointer}
button:hover{border-color:#2548ff;color:#2548ff} .sup:hover{border-color:#d1344b;color:#d1344b}
</style></head><body>
<h1>Modération des retours</h1>
<p class="att">${enLigne} message${enLigne > 1 ? 's' : ''} en ligne. Les messages sont publiés dès leur envoi&nbsp;: cet écran sert à retirer.</p>
<p style="font-size:.85rem;color:#64748b">Retirer sans hésiter un message qui met en cause un établissement nommément,
ou qui permet d’identifier une personne — résident, proche, salarié. Le retrait doit être <b>prompt</b>&nbsp;:
c’est la condition du régime de responsabilité limitée de l’hébergeur.</p>
${lignes.map(bloc).join('')}
<script>
const CLE = ${JSON.stringify(cle)};
document.addEventListener('click', async (e) => {
  const b = e.target.closest('button'); if (!b) return;
  b.disabled = true;
  const url = b.dataset.sup ? '/admin/supprime' : '/admin/etat';
  await fetch(url + '?cle=' + encodeURIComponent(CLE), {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id: +b.dataset.id, etat: b.dataset.etat }),
  });
  location.reload();
});
<\/script></body></html>`;
}

export default {
  async fetch(requete, env) {
    const url = new URL(requete.url);

    if (requete.method === 'OPTIONS') return new Response(null, { headers: entetes() });

    // ── Les messages publiés, lus par la page publique
    if (requete.method === 'GET' && url.pathname === '/messages') {
      const { results } = await env.DB.prepare(
        `SELECT id, nom, message, publie_le FROM retours
         WHERE etat = 'publie' ORDER BY publie_le DESC LIMIT 200`).all();
      return new Response(JSON.stringify({ messages: results }), {
        headers: entetes({ 'Cache-Control': 'public, max-age=300' }),
      });
    }

    // ── Dépôt d'un message
    if (requete.method === 'POST' && url.pathname === '/messages') {
      let d;
      try { d = await requete.json(); } catch (e) { return repond({ erreur: 'format' }, 400); }

      // Piège à robots : un champ invisible qu'un humain ne remplit jamais.
      // Préféré à un captcha, qui ajouterait un traceur tiers sur la page.
      // On répond « ok » sans rien enregistrer : signaler le rejet apprendrait
      // au robot comment le contourner.
      if (d.site) return repond({ ok: true });
      if (!d.depuis || Date.now() - Number(d.depuis) < DELAI_MINI_MS) return repond({ ok: true });

      const message = nettoie(d.message, MAX_MESSAGE);
      const nom = nettoie(d.nom, MAX_NOM);
      if (message.length < 10) return repond({ erreur: 'court' }, 400);

      const ip = requete.headers.get('CF-Connecting-IP') || '';
      const emp = await empreinte(ip, env.SEL_IP || 'sel');
      const { results: recents } = await env.DB.prepare(
        `SELECT COUNT(*) AS n FROM retours WHERE empreinte = ? AND recu_le > datetime('now','-1 hour')`)
        .bind(emp).all();
      if (recents[0].n >= PAR_HEURE) return repond({ erreur: 'trop' }, 429);

      // Publication immédiate : le retrait se fait après coup, depuis l'écran de
      // modération. Les barrières anti-robots restent en amont — elles évitent le
      // spam automatisé, qui est le seul volume qu'un humain ne peut pas suivre.
      await env.DB.prepare(
        `INSERT INTO retours (nom, message, etat, recu_le, publie_le, empreinte)
         VALUES (?, ?, 'publie', datetime('now'), datetime('now'), ?)`)
        .bind(nom || null, message, emp).run();
      return repond({ ok: true });
    }

    // ── Modération : tout ce qui suit exige le secret
    const secret = url.searchParams.get('cle') || requete.headers.get('X-Cle') || '';
    if (!env.CLE_ADMIN || secret !== env.CLE_ADMIN) return repond({ erreur: 'refuse' }, 403);

    // L'écran de modération est servi par le Worker lui-même : rien n'est publié
    // sur le site, et la même origine évite tout échange inter-domaines.
    if (requete.method === 'GET' && url.pathname === '/admin') {
      const { results } = await env.DB.prepare(
        `SELECT id, nom, message, etat, recu_le FROM retours ORDER BY
           CASE etat WHEN 'publie' THEN 0 ELSE 1 END, recu_le DESC
         LIMIT 300`).all();
      return new Response(pageAdmin(results, secret), {
        headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store',
                   'X-Robots-Tag': 'noindex, nofollow' },
      });
    }
    if (url.pathname === '/admin/liste') {
      const { results } = await env.DB.prepare(
        `SELECT id, nom, message, etat, recu_le FROM retours ORDER BY recu_le DESC LIMIT 300`).all();
      return repond({ messages: results });
    }
    if (requete.method === 'POST' && url.pathname === '/admin/etat') {
      const d = await requete.json();
      const etats = ['attente', 'publie', 'refuse'];
      if (!etats.includes(d.etat)) return repond({ erreur: 'etat' }, 400);
      await env.DB.prepare(
        `UPDATE retours SET etat = ?,
           publie_le = CASE WHEN ? = 'publie' THEN datetime('now') ELSE publie_le END
         WHERE id = ?`).bind(d.etat, d.etat, d.id).run();
      return repond({ ok: true });
    }
    if (requete.method === 'POST' && url.pathname === '/admin/supprime') {
      const d = await requete.json();
      await env.DB.prepare('DELETE FROM retours WHERE id = ?').bind(d.id).run();
      return repond({ ok: true });
    }
    return repond({ erreur: 'inconnu' }, 404);
  },

  /** Ménage quotidien : les empreintes ne servent qu'à limiter le débit sur une
      heure, et les messages refusés n'ont aucune raison d'être conservés. */
  async scheduled(evt, env) {
    await env.DB.prepare(
      `UPDATE retours SET empreinte = NULL WHERE recu_le < datetime('now','-2 days')`).run();
    await env.DB.prepare(
      `DELETE FROM retours WHERE etat = 'refuse' AND recu_le < datetime('now','-30 days')`).run();
  },
};
