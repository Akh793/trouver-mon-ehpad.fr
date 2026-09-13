# -*- coding: utf-8 -*-
"""Génère /retours/ : la page où les visiteurs écrivent, et où les messages publiés s'affichent.

Cette page est la seule du site qui transmette quelque chose. Tout le reste du
parcours calcule dans le navigateur et l'affirme ; il fallait donc que la
différence soit dite ici, en haut, sans détour.

Elle est construite à part de build_pages.py, qui s'interdit tout JavaScript :
le dépôt d'un message et l'affichage des messages publiés en demandent.
"""
import os, re, json

SITE = '../site'
FONT = open('fontface.css', encoding='utf-8').read()
CSS = open('site.css', encoding='utf-8').read()

# Adresse du point de réception. À remplacer après le déploiement du Worker
# (voir worker/LISEZMOI.md). Tant qu'elle vaut cette valeur, le formulaire
# affiche que l'envoi n'est pas encore actif plutôt que d'échouer en silence.
API = 'https://retours-tme.trouver-mon-ehpad.workers.dev'

CORPS = """
<p class="lead">Ce site est fait pour des familles qui cherchent une place, souvent dans l’urgence.
Ce qui vous a servi, ce qui vous a manqué, ce qui vous a induit en erreur : écrivez-le ici.</p>

<div class="avert">
  <p><b>Cette page est la seule du site qui transmette quelque chose.</b> Le calculateur, lui, travaille
  entièrement dans votre navigateur. Ici, votre message part sur un serveur pour être lu.</p>
  <p><b>N’écrivez pas de données personnelles</b> — ni les vôtres, ni celles d’un proche : pas de nom
  de résident, pas d’état de santé, pas de ressources, pas d’adresse ni de numéro de téléphone.
  Pour une situation particulière, écrivez plutôt à <a href="mailto:contact@trouver-mon-ehpad.fr">contact@trouver-mon-ehpad.fr</a>.</p>
  <p><b>Votre message apparaît aussitôt.</b> Il n’est pas relu avant. En retour, tout message peut être
  retiré : celui qui met en cause un établissement nommément, celui qui permet d’identifier une personne —
  un résident, un proche, un salarié — et tout contenu manifestement illicite. Chaque message porte un
  lien pour le signaler.</p>
</div>

<h2>Écrire un message</h2>
<form id="form-retour" novalidate>
  <div class="fld">
    <label for="r-message">Votre message</label>
    <textarea id="r-message" rows="6" maxlength="1500" required
      placeholder="Ce qui vous a aidé, ce qui manquait, ce qui n’était pas clair…"></textarea>
    <p class="fld-h"><span id="r-reste">1500</span> caractères restants.</p>
  </div>
  <div class="fld">
    <label for="r-nom">Prénom ou pseudonyme <span class="opt">— facultatif</span></label>
    <input id="r-nom" maxlength="40" autocomplete="off" placeholder="Marie, un aidant, …">
    <p class="fld-h">Affiché tel quel. Laissez vide pour rester anonyme.</p>
  </div>
  <div class="piege" aria-hidden="true">
    <label for="r-site">Ne pas remplir</label>
    <input id="r-site" tabindex="-1" autocomplete="off">
  </div>
  <button type="submit" class="btn" id="r-envoi">Envoyer</button>
  <p id="r-etat" class="r-etat" role="status" hidden></p>
</form>

<h2>Ce que les visiteurs ont écrit</h2>
<div id="r-liste" class="r-liste"><p class="muted">Chargement des messages…</p></div>
<p class="f-src" style="max-width:46rem;margin-inline:auto">Les messages sont écrits par des visiteurs et publiés sans relecture préalable.
Ils n’engagent qu’eux et n’ont pas été vérifiés. Un message vous paraît inexact, diffamatoire, ou
révèle l’identité de quelqu’un&nbsp;? Utilisez le lien «&nbsp;Signaler&nbsp;» qui l’accompagne, ou écrivez à
<a href="mailto:contact@trouver-mon-ehpad.fr?subject=Signalement%20d%27un%20message">contact@trouver-mon-ehpad.fr</a>&nbsp;:
il sera retiré s’il doit l’être.</p>
"""

SCRIPT = """
(function () {
  var API = '__API__';
  var actif = API.indexOf('VOTRE-SOUS-DOMAINE') < 0;
  var f = document.getElementById('form-retour');
  var msg = document.getElementById('r-message');
  var reste = document.getElementById('r-reste');
  var etat = document.getElementById('r-etat');
  var liste = document.getElementById('r-liste');
  var depuis = Date.now();

  function dit(t, cls) { etat.textContent = t; etat.className = 'r-etat ' + (cls || ''); etat.hidden = false; }

  msg.addEventListener('input', function () { reste.textContent = 1500 - msg.value.length; });

  f.addEventListener('submit', async function (e) {
    e.preventDefault();
    var t = msg.value.trim();
    if (t.length < 10) { dit('Le message est trop court.', 'err'); msg.focus(); return; }
    if (!actif) { dit('L’envoi de messages n’est pas encore actif sur ce site.', 'err'); return; }
    var b = document.getElementById('r-envoi');
    b.disabled = true; dit('Envoi…');
    try {
      var rep = await fetch(API + '/messages', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: t, nom: document.getElementById('r-nom').value.trim(),
                               site: document.getElementById('r-site').value, depuis: depuis }),
      });
      var d = await rep.json();
      if (d.erreur === 'trop') { dit('Trop de messages envoyés depuis cet appareil. Réessayez plus tard.', 'err'); }
      else if (d.erreur) { dit('L’envoi n’a pas abouti. Réessayez, ou écrivez à contact@trouver-mon-ehpad.fr', 'err'); }
      else {
        f.reset(); reste.textContent = '1500';
        dit('Message publié. Merci. Rechargez la page pour le voir apparaître.', 'ok');
      }
    } catch (err) {
      dit('L’envoi n’a pas abouti. Vérifiez votre connexion, ou écrivez à contact@trouver-mon-ehpad.fr', 'err');
    }
    b.disabled = false;
  });

  function esc(t) {
    return String(t == null ? '' : t).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function dateFr(s) {
    if (!s) return '';
    var p = String(s).slice(0, 10).split('-');
    return p.length === 3 ? p[2] + '/' + p[1] + '/' + p[0] : '';
  }

  if (!actif) { liste.innerHTML = '<p class="muted">Les messages s’afficheront ici.</p>'; return; }
  fetch(API + '/messages').then(function (r) { return r.json(); }).then(function (d) {
    var m = (d && d.messages) || [];
    if (!m.length) { liste.innerHTML = '<p class="muted">Aucun message publié pour l’instant.</p>'; return; }
    liste.innerHTML = m.map(function (x) {
      // Le lien de signalement porte l'identifiant du message : sans lui, une
      // demande de retrait ne désigne rien de précis et ne peut pas être traitée.
      var sujet = encodeURIComponent('Signalement du message n° ' + x.id);
      return '<article class="r-m"><p class="r-h">' + (x.nom ? '<b>' + esc(x.nom) + '</b> · ' : '')
        + dateFr(x.publie_le) + ' · <a class="r-sig" href="mailto:contact@trouver-mon-ehpad.fr?subject='
        + sujet + '">Signaler</a></p><p class="r-t">' + esc(x.message) + '</p></article>';
    }).join('');
  }).catch(function () {
    liste.innerHTML = '<p class="muted">Les messages n’ont pas pu être chargés.</p>';
  });
})();
"""

STYLE = """
/* Ces règles ne valent que pour cette page : elles sont écrites dans son corps,
   pas dans la feuille partagée. */
.page{margin-inline:auto;max-width:62rem}
/* Le header garde toute la largeur : le bouton de thème y vit, et il doit rester
   au bord droit de la fenêtre. Seul son contenu textuel est centré. */
#layout header{text-align:center}
#layout header .fil{display:block}
.lead{font-size:1.05rem;color:var(--mut);max-width:62ch;margin-inline:auto;text-align:center}
/* Trois mises en garde côte à côte plutôt qu'empilées : même texte, trois fois
   moins de hauteur, et chacune se lit d'un coup d'œil. */
.avert{margin:1.6rem auto;padding:1.1rem 1.3rem;border-radius:var(--r2);background:var(--ti-or);
  border:1px solid var(--bd2);font-size:.88rem;line-height:1.5;
  display:grid;gap:1rem 1.6rem;grid-template-columns:repeat(auto-fit,minmax(16rem,1fr))}
.avert p{margin:0}
.page h2{text-align:center}
#form-retour{max-width:40rem;margin:.8rem auto 0}
#form-retour .fld{margin-bottom:1rem}
#form-retour button{display:block;margin-inline:auto}
#form-retour textarea{width:100%;border:1.5px solid var(--bd);border-radius:var(--r2);
  background:var(--surf);padding:.7rem .9rem;font:inherit;font-size:1rem;color:inherit;margin-top:.3rem;resize:vertical}
#form-retour textarea:focus{outline:none;border-color:var(--bl-t);box-shadow:0 0 0 4px rgba(37,72,255,.14)}
.opt{font-weight:400;color:var(--mut2)}
/* Piège à robots : hors écran, hors tabulation, hors lecteur d'écran.
   Préféré à un captcha, qui ajouterait un service tiers sur la page. */
.piege{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
.r-etat{margin:.8rem auto 0;padding:.6rem .9rem;border-radius:var(--r2);font-size:.9rem;max-width:40rem;text-align:center}
.r-etat.ok{background:var(--ti-ve);color:var(--sur-ve)}
.r-etat.err{background:var(--ti-ro);color:var(--sur-ro)}
.r-liste{margin-top:.8rem;display:grid;gap:.8rem;max-width:46rem;margin-inline:auto}
.r-m{border:1px solid var(--bd2);border-left:4px solid var(--bd);border-radius:var(--r2);padding:.8rem 1rem;background:var(--surf)}
.r-h{margin:0 0 .4rem;font-size:.8rem;color:var(--mut2)}
.r-sig{color:var(--mut2);text-decoration:underline}
.r-sig:hover{color:var(--sur-ro)}
.r-t{margin:0;white-space:pre-wrap;line-height:1.55}
"""


def main():
    import build_pages as bp
    corps = CORPS + '<style>' + STYLE + '</style>\n<script>' + SCRIPT.replace('__API__', API) + '</script>'
    html = bp.HEAD.format(
        title='Vos retours sur le site | Trouver mon EHPAD',
        desc='Écrivez ce qui vous a aidé et ce qui vous a manqué sur trouver-mon-ehpad.fr. '
             'Les messages sont lus avant publication.',
        slug='retours/', robots='index, follow', h1='Vos retours',
        body=corps, font=FONT, css=CSS, jsonld=bp.crumb('Vos retours', 'retours/'))
    os.makedirs(os.path.join(SITE, 'retours'), exist_ok=True)
    open(os.path.join(SITE, 'retours', 'index.html'), 'w', encoding='utf-8').write(html)
    print('page /retours/ écrite :', len(html.encode()), 'octets ;',
          'envoi', 'ACTIF' if 'VOTRE-SOUS-DOMAINE' not in API else 'EN ATTENTE du déploiement du Worker')


if __name__ == '__main__':
    main()
