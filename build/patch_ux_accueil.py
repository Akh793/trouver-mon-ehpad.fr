# -*- coding: utf-8 -*-
"""Refonte de la page d'accueil, lot 1 (29/09/2026) : P0 + P1 + P2 du brainstorm
claude/ux-accueil-brainstorm-v1.md, décisions validées par l'éditeur.

P0 — défauts
  · « Calculermon reste à charge » : l'espace de tête d'un élément flex est avalé → &nbsp;.
  · Logo mobile tronqué en « Trouver mon » (« EHPAD » masqué sous 420 px) → nom entier.
  · Résumés dépliables écrasés en colonne sur mobile (inline-flex) → flex avec retour à la ligne.
  · Noms FINESS bruts ou collés (« …DÉPENDANTESLOUISE-THÉRÈSE ») → nomLisible(), règle identique
    à build/seo (7 417 noms comparés, 0 écart).
  · « Imprimer » affiché avant tout résultat → masqué tant qu'il n'y a rien à imprimer.
  · Bandeau de consentement : il protège un identifiant Google Tag Manager VIDE et cachait le
    formulaire. Il ne s'affiche plus que si ME_GTM_ID est renseigné (décision de l'éditeur).
  · La mini-grille d'autonomie se refermait dès la première case cochée (state.gir passait de
    « ? » à « 34 », et le panneau n'était visible que pour « ? ») : impossible d'atteindre GIR 1-2.

P1 — premier écran et formulaire
  · En-tête : 9 pastilles de navigation retirées (elles restent dans « Naviguer » et le pied de
    page), encart professionnel réduit à un lien, une seule ligne de sous-titre, H1 qui nomme le
    livrable. « Comparer vos devis » garde un lien au premier écran (choix P4 du lot SEO).
  · Trois questions : où, quelles ressources, quelle autonomie. « Distance » et « Ce qui compte »
    quittent le formulaire : la barre des résultats les porte déjà (rayon, tri). Le tri « Aide
    sociale possible d'abord » y est ajouté pour ne rien perdre.
  · Autonomie : situations concrètes d'abord, GIR notifié ensuite ; plus de présélection
    silencieuse (état initial « ? », calcul sur GIR 3-4 DIT dans le résultat).
  · Exemples sous les champs au lieu de placeholders qui ressemblaient à des valeurs.
  · Typographie du formulaire : libellés 17 px, aides 15 px, boutons 15 px, cibles de 44 px.

P2 — la réponse en tête
  · Avec des ressources : le chiffre principal devient ce qui manque (ou le nombre
    d'établissements couverts), plus le nombre d'établissements.
  · Chaque carte dit « Il manque X €/mois » ou « Couvert par les ressources ».
  · Les 10 % laissés pour les dépenses personnelles (au moins 125 €) sont écrits à côté du
    montant : sans eux, 2 094 − 1 500 ne donnait pas les 744 € affichés.
  · Mobile : la liste d'abord, la carte sur demande.
  · Après le premier résultat, une invite à préciser épargne, couple, enfants.
"""
import io, os, sys

B = os.path.dirname(os.path.abspath(__file__))
n = 0


def patch(rel, paires):
    global n
    p = os.path.join(B, rel)
    s = io.open(p, encoding='utf-8').read()
    for a, b in paires:
        if s.count(a) != 1:
            print('ANCRE %s dans %s :' % ('INTROUVABLE' if not s.count(a) else 'MULTIPLE', rel),
                  a[:120].replace('\n', ' '))
            sys.exit(1)
        s = s.replace(a, b, 1)
        n += 1
    io.open(p, 'w', encoding='utf-8').write(s)


# ─────────────────────────────── GABARIT ───────────────────────────────
patch('index.template.html', [
    # P0 — espace avalé dans le bouton de la barre
    ('Calculer<span class="tb-cta-plus"> mon reste à charge</span>',
     'Calculer<span class="tb-cta-plus">&nbsp;mon reste à charge</span>'),

    # P1 — H1 : le livrable, pas l'activité
    ('<h1 id="h1-titre">Trouvez un EHPAD<br><span class="h1-l2">et <em class="bl">estimez</em> son <em class="co">coût</em></span></h1>',
     '<h1 id="h1-titre">Le coût d’un EHPAD<br><span class="h1-l2"><em class="bl">aides</em> <em class="co">déduites</em></span></h1>'),

    # P1 — l'encart professionnel devient un lien
    ('<a href="/professionnels/" class="lien-pro">Vous accompagnez des personnes âgées&nbsp;?<b>Espace professionnel</b></a>',
     '<a href="/professionnels/" class="lien-pro">Espace professionnel</a>'),

    # P1 — une ligne de sous-titre, les pastilles retirées, le lien devis gardé
    ('''    <p class="sub">Comparez les établissements dans la zone de votre choix.<br><span class="sub2">Précisez votre situation pour estimer votre budget mensuel. Gratuit, sans inscription.</span></p>
    <nav aria-label="Navigation principale" class="nav print-hide">
      <a href="#bande-carte">La carte des restes à charge</a>
      <a href="/comparer-devis-ehpad/" class="nav-devis">Comparer vos devis</a>
      <a href="/ehpad/">Les EHPAD en France</a>
      <a href="/prix-ehpad/">Prix des EHPAD</a>
      <a href="/aides-ehpad/">Aides financières</a>
      <a href="/guides/">Guides</a>
      <a href="notre-methodologie.html">Méthodologie</a>
      <a href="#bande-faq">Questions fréquentes</a>
      <a href="/retours/" class="nav-avis">Vos retours</a>
    </nav>''',
     '''    <p class="sub">Ce qui resterait à payer chaque mois, établissement par établissement. Gratuit, sans inscription.</p>
    <p class="sub-devis print-hide">Vous avez déjà des devis&nbsp;? <a href="/comparer-devis-ehpad/">Comparez-les ligne à ligne</a></p>'''),

    # P1 — trois questions ; P0 — la mini-grille ne se referme plus
    ('''    <div class="grid4">
      <div class="fld">
        <label for="cp">Code postal recherché</label>
        <input id="cp" inputmode="numeric" maxlength="5" placeholder="69003" autocomplete="postal-code" aria-describedby="cp-aide">
        <div id="commune" class="fld-ok"></div>
        <div id="cp-dd" class="dd" hidden></div>
        <p id="cp-aide" class="fld-h">La zone où vous cherchez un établissement.</p>
      </div>
      <div class="fld">
        <label for="rayon">Distance autour de ce lieu</label>
        <select id="rayon">
          <option value="10">10 km</option>
          <option value="20" selected>20 km</option>
          <option value="40">40 km</option>
          <option value="60">60 km</option>
        </select>
        <p class="fld-h">Distance à vol d’oiseau, pas par la route.</p>
      </div>
      <div class="fld">
        <label id="lbl-gir">Niveau de dépendance (GIR)</label>
        <div class="seg seg4" data-seg="gir:12,34,56,?" role="group" aria-label="Groupe iso-ressources">
          <button type="button">GIR 1-2</button><button type="button">GIR 3-4</button><button type="button">GIR 5-6</button><button type="button">Je ne sais pas</button>
        </div>
        <p class="fld-h">Si un GIR a déjà été attribué, indiquez-le ici.</p>
      </div>
      <div class="fld">
        <label for="revenus" id="lbl-revenus">Retraites et pensions du parent</label>
        <div class="in-eur"><input id="revenus" inputmode="numeric" placeholder="1 600"><span>€/mois</span></div>
        <p class="fld-h">Montant mensuel perçu, toutes pensions confondues.</p>
      </div>
    </div>

    <div id="gir-aide" hidden class="gir-box">
      <p><b>Quatre questions pour situer le GIR</b> — estimation indicative, jamais la notification officielle.</p>
      <div id="gir-calc" class="gir-q">
        <label><input type="checkbox"> Il ou elle a besoin d’aide pour se lever et se déplacer</label>
        <label><input type="checkbox"> Il ou elle a besoin d’aide pour s’habiller ou faire sa toilette</label>
        <label><input type="checkbox"> Il ou elle a besoin d’aide pour manger</label>
        <label><input type="checkbox"> Il ou elle se repère mal dans le temps ou dans l’espace</label>
      </div>
      <p id="gir-res" class="fld-h"></p>
    </div>
''',
     '''    <div class="grid4 grid-q">
      <div class="fld">
        <label for="cp">Code postal de la zone recherchée</label>
        <input id="cp" inputmode="numeric" maxlength="5" autocomplete="postal-code" aria-describedby="cp-aide">
        <div id="commune" class="fld-ok"></div>
        <div id="cp-dd" class="dd" hidden></div>
        <p id="cp-aide" class="fld-h">Exemple&nbsp;: 69003. Rayon de 20&nbsp;km, modifiable ensuite.</p>
      </div>
      <div class="fld">
        <label for="revenus" id="lbl-revenus">Retraites et pensions du proche, par mois</label>
        <div class="in-eur"><input id="revenus" inputmode="numeric" aria-describedby="rev-aide"><span>€/mois</span></div>
        <p id="rev-aide" class="fld-h">Montant net perçu, toutes pensions confondues. Exemple&nbsp;: 1&nbsp;600&nbsp;€.</p>
      </div>
      <fieldset class="fld fld-gir">
        <legend id="lbl-gir">Au quotidien, votre proche a-t-il besoin d’aide pour…</legend>
        <div id="gir-calc" class="gir-q">
          <label><input type="checkbox" value="lever"> se lever et se déplacer</label>
          <label><input type="checkbox" value="toilette"> s’habiller ou faire sa toilette</label>
          <label><input type="checkbox" value="manger"> manger</label>
          <label><input type="checkbox" value="reperes"> se repérer dans le temps ou l’espace</label>
          <label class="gir-aucun"><input type="checkbox" value="aucun"> aucune de ces aides</label>
        </div>
        <p id="gir-res" class="fld-h" aria-live="polite"></p>
        <details class="gir-notif" id="gir-notif">
          <summary>Un niveau GIR a déjà été notifié&nbsp;?</summary>
          <div class="seg" data-seg="girNotif:12,34,56" role="group" aria-label="GIR notifié par le département">
            <button type="button">GIR 1-2</button><button type="button">GIR 3-4</button><button type="button">GIR 5-6</button>
          </div>
        </details>
      </fieldset>
    </div>
'''),

    # un exemple sous le champ plutôt qu'une valeur fantôme dans le champ
    ('''<div class="in-eur"><input id="epargne" inputmode="numeric" placeholder="30 000"><span>€</span></div>
        <p class="fld-h">Pour estimer combien de temps elle peut compléter le budget.</p>''',
     '''<div class="in-eur"><input id="epargne" inputmode="numeric"><span>€</span></div>
        <p class="fld-h">Pour estimer combien de temps elle peut compléter le budget. Exemple&nbsp;: 30&nbsp;000&nbsp;€.</p>'''),

    # P1 — « Ce qui compte » quitte le formulaire : le tri des résultats le porte
    ('''    <div class="fld prio-fld">
      <label>Qu’est-ce qui compte le plus pour vous&nbsp;?</label>
      <div class="seg seg4" data-seg="priorite:rac,dist,ash,has" role="group" aria-label="Ce qui compte le plus">
        <button type="button">Le budget</button><button type="button">La proximité</button><button type="button">Les aides</button><button type="button">La qualité</button>
      </div>
      <p class="fld-h">Change l’ordre des résultats, pas la liste.</p>
    </div>
''', ''),
    ('''                <option value="has">Qualité</option>
                <option value="evol">''',
     '''                <option value="has">Qualité</option>
                <option value="ash">Aide sociale possible d’abord</option>
                <option value="evol">'''),

    # P2 — mobile : la liste d'abord, la carte sur demande
    ('''                <button type="button" data-vue="carte" aria-pressed="true">Carte</button>
                <button type="button" data-vue="fiche" aria-pressed="false">Fiche</button>
              </div>''',
     '''                <button type="button" data-vue="carte" aria-pressed="true">Carte</button>
                <button type="button" data-vue="fiche" aria-pressed="false">Fiche</button>
              </div>
              <button type="button" id="carte-mob" class="btn-f carte-mob" aria-pressed="false" aria-controls="pan-carte">Voir sur la carte</button>'''),

    # P2 — invite à préciser après le premier résultat
    ('''            <button type="button" id="share-btn" class="btn-sec">🔗 Copier le lien</button>
          </div>''',
     '''            <button type="button" id="affiner-btn" class="btn-sec" hidden>Épargne, couple, enfants&nbsp;: affiner</button>
            <button type="button" id="share-btn" class="btn-sec">🔗 Copier le lien</button>
          </div>'''),

    # P0 — rien à imprimer avant un résultat
    ('<button type="button" id="print-btn" class="btn-sec" data-print>Imprimer</button>',
     '<button type="button" id="print-btn" class="btn-sec" data-print hidden>Imprimer</button>'),

    # P0 — le bandeau ne demande plus un accord pour un outil absent
    ("    if (!ME_consent.get()) show();",
     "    // Aucun outil soumis à consentement tant que ME_GTM_ID est vide : ni bandeau, ni lien\n"
     "    // « Gérer les cookies ». Le relevé d'audience du site est sans cookie ni identifiant.\n"
     "    if (!window.ME_GTM_ID) { document.querySelectorAll('[data-consent-open]').forEach(function(a){a.hidden=true;}); return; }\n"
     "    if (!ME_consent.get()) show();"),
])

# ─────────────────────────────── FEUILLE DE STYLE ───────────────────────────────
patch('site.css', [
    # P0 — résumés dépliables : le texte passe à la ligne au lieu de s'écraser en colonne
    ('.bloc-plus>summary{cursor:pointer;list-style:none;padding:.7rem 0;font-size:.95rem;display:inline-flex;align-items:center;gap:.4rem}',
     '.bloc-plus>summary{cursor:pointer;list-style:none;padding:.7rem 0;font-size:.95rem;display:flex;flex-wrap:wrap;align-items:baseline;gap:.1rem .4rem}'),
    # P0 — le logo garde son nom entier sur mobile
    ('@media (max-width:420px){.tb-logo span{display:none}}',
     '@media (max-width:420px){.tb-logo{font-size:.9rem}}'),
])

CSS_FIN = '''
/* ---------- Refonte de l'accueil, lot 1 (29/09/2026) ----------
   Portée limitée à l'accueil (#bande-situation, en-tête, résultats) : site.css sert aussi
   les pages de contenu, qui ne doivent pas bouger. */
.sub-devis{margin-top:.5rem;font-size:.95rem;color:var(--mut)}
.sub-devis a{color:var(--bl-t);font-weight:600;text-underline-offset:3px}
body.explore header .sub-devis{display:none}
.lien-pro{text-align:right;font-size:.85rem;font-weight:600;color:var(--bl-t);border:0;background:none;padding:0}
.lien-pro::after{content:' →';font-weight:400}
@media (max-width:640px){
  .head-side{flex-direction:row;flex-wrap:wrap;align-items:center;gap:.4rem 1rem}
  .lien-pro{text-align:left;align-self:auto}
}
/* Formulaire : trois questions, lisibles par un lecteur de 60 ans et plus. */
#bande-situation .grid-q{grid-template-columns:repeat(2,minmax(0,1fr))}
#bande-situation .grid-q .fld-gir{grid-column:1 / -1}
#bande-situation .grid4 .fld label,#bande-situation .grid3 .fld label,#bande-situation .fld-gir legend{font-size:1.06rem;line-height:1.3}
#bande-situation .grid4 .fld label,#bande-situation .grid3 .fld label{min-height:0}
#bande-situation .fld-h{font-size:.94rem;line-height:1.4;color:var(--mut)}
#bande-situation input,#bande-situation select{font-size:1.06rem;min-height:48px}
#bande-situation .seg button{font-size:.94rem;min-height:44px}
.fld-gir{margin:0}
.fld-gir legend{float:left;width:100%;padding:0;font-weight:600;color:var(--ink)}
.fld-gir legend+*{clear:both}
#gir-calc{margin-top:.7rem;display:grid;gap:.5rem;grid-template-columns:repeat(auto-fit,minmax(11rem,1fr))}
#bande-situation #gir-calc label{display:flex;align-items:center;gap:.6rem;min-height:48px;padding:.55rem .8rem;border:1.5px solid var(--bd);border-radius:var(--r2);background:var(--surf);font-size:1rem;font-weight:500;color:var(--ink);cursor:pointer}
#bande-situation #gir-calc label:has(input:checked){border-color:var(--bl-t);background:var(--ti-bl)}
#gir-calc input{width:1.25rem;height:1.25rem;min-height:0;margin:0;flex:0 0 auto;accent-color:var(--bl)}
.gir-notif{margin-top:.7rem}
.gir-notif summary{cursor:pointer;font-size:.94rem;color:var(--bl-t);font-weight:600;min-height:44px;display:flex;align-items:center}
.gir-notif .seg{max-width:26rem}
@media (max-width:640px){
  #bande-situation .grid-q{grid-template-columns:minmax(0,1fr)}
  #gir-calc{grid-template-columns:minmax(0,1fr)}
}
/* Résultat : ce qui manque, dit sur chaque carte. */
.res-m .manque{display:block;margin-top:.3rem;font-size:.86rem;font-weight:700;white-space:normal}
.res-m .manque.ok{color:var(--sur-ve)}
/* Mobile : la liste d'abord ; la carte s'ouvre sur demande. */
.carte-mob{display:none}
@media (max-width:1039px){
  .seg-vue{display:none}
  .carte-mob{display:inline-flex;align-items:center}
  .carte-mob[aria-pressed="true"]{border-color:var(--bl-t);color:var(--bl-t)}
  .atelier:not(.carte-on) #pan-carte{display:none}
}
'''
p = os.path.join(B, 'site.css')
s = io.open(p, encoding='utf-8').read()
if 'Refonte de l\'accueil, lot 1' not in s:
    io.open(p, 'w', encoding='utf-8').write(s.rstrip('\n') + '\n' + CSS_FIN)
    n += 1

print('patch_ux_accueil (gabarit + CSS) :', n, 'remplacements')


# ─────────────────────────────── APPLICATION ───────────────────────────────
APP = os.path.join('..', 'site', 'app.js')
patch(APP, [
    # P1 — aucune présélection silencieuse du GIR
    ("    gir: '34',\n    revenus: NaN",
     "    gir: '?',                  // aucune présélection : sans réponse, le calcul retient GIR 3-4 et le dit\n"
     "    girNotif: null,            // GIR notifié par le département, s'il y en a un\n"
     "    girCases: [false, false, false, false, false],   // mini-grille : lever, toilette, manger, repères, aucune\n"
     "    revenus: NaN"),

    # mesure du parcours : une fiche ouverte est la troisième étape
    ("      if (pro() && PRO_EVT[nom]) nom = PRO_EVT[nom];",
     "      if (nom === 'result_opened' && window.ME_etape) window.ME_etape('f');\n"
     "      if (pro() && PRO_EVT[nom]) nom = PRO_EVT[nom];"),

    # P2 — ce qui est laissé à la personne, exposé pour être écrit à côté du montant
    ("      moisEpargne, couleur, ash, famille, secteur, vieux, notes,\n    };",
     "      moisEpargne, couleur, ash, famille, secteur, vieux, notes,\n"
     "      gardeMini, reserveConjoint,   // laissé à la personne avant de compter ce qui manque\n    };"),

    # P2 — la carte mobile se recadre quand on l'ouvre
    ("  let map = null, layer = null, cluster = null, leafletPromise = null;",
     "  let map = null, layer = null, cluster = null, leafletPromise = null;\n"
     "  let bornesCarte = null;   // dernier cadrage : la carte masquée sur mobile se recadre à l'ouverture"),
    ("      map.fitBounds(b.pad(0.12));\n    } else map.setView([s.commune.lat, s.commune.lon], 11);",
     "      bornesCarte = b.pad(0.12);\n      map.fitBounds(bornesCarte);\n"
     "    } else { bornesCarte = null; map.setView([s.commune.lat, s.commune.lon], 11); }"),

    # P2 — la carte de résultat dit ce qui manque
    ("      if (r.chambreSupposee) second += '<span class=\"tarif t-reserve\">tarif de chambre double non déclaré</span>';\n",
     "      if (r.chambreSupposee) second += '<span class=\"tarif t-reserve\">tarif de chambre double non déclaré</span>';\n"
     "      // Ce qui manque chaque mois, sur la carte même : la couleur seule ne disait pas combien.\n"
     "      // Facture incomplète : un manque devient un minimum, et « couvert » n'est pas affirmé.\n"
     "      if (r.trou > 0) second += `<span class=\"manque\">Il manque ${r.depConnue ? '' : 'au moins '}${euro(r.trou)}/mois`\n"
     "        + `${r.couleur === 'orange' ? ` · l’épargne tient ${Math.floor(r.moisEpargne / 12)} ans` : ''}</span>`;\n"
     "      else if (r.depConnue) second += '<span class=\"manque ok\">Couvert par les ressources</span>';\n"),

    # le GIR non renseigné est dit une fois en tête des résultats, plus sur chaque carte
    ("      else if (r.girSuppose) second += '<span class=\"tarif t-reserve\">niveau d’autonomie supposé</span>';\n",
     "      // GIR non renseigné : dit une fois, en tête des résultats, plutôt que sur chaque carte\n"),

    # P2 — la fiche explique l'écart entre « facture − retraite » et « à compléter »
    ("          Après les revenus renseignés${state.epargne > 0",
     "          Ressources moins ${euro(r.gardeMini)} laissés pour ${mot('possessif')} dépenses personnelles"
     "${r.reserveConjoint ? ` et ${euro(r.reserveConjoint)} pour le conjoint à domicile` : ''}${state.epargne > 0"),

    # P0 — « Imprimer » n'apparaît qu'avec un résultat
    ("    $('route-wrap').hidden = !pret; $('route-vide').hidden = pret;",
     "    $('route-wrap').hidden = !pret; $('route-vide').hidden = pret; $('print-btn').hidden = !pret;"),

    # P2 — la réponse en tête
    ("""    // Le nombre d'établissements devient le chiffre de tête : c'est lui le résultat
    // de la recherche. La médiane le suit comme repère, jamais comme un prix.
    $('res-titre').textContent = 'Les EHPAD dans cette zone';
    $('res-chiffre').textContent = `${list.length} établissement${list.length > 1 ? 's' : ''}`;
    const sansTarif = list.length - avecPrix.length;
    if (med == null) {
      $('res-sous').innerHTML = `à ${s.rayon} km ${esc(de(s.commune.nom))} · aucun n’a déclaré son tarif`;
    } else {
      // Le mot dit ce que le chiffre mesure : un tarif affiché, ou un budget calculé.
      const lib = p ? 'Budget médian estimé' : 'Prix médian de la sélection';
      $('res-sous').innerHTML = `à ${s.rayon} km ${esc(de(s.commune.nom))}`
        + ` · <b>${lib}&nbsp;: ${euro(med)}</b>/mois, de ${euro(mini)} à ${euro(maxi)}`
        + ` sur ${avecPrix.length} établissement${avecPrix.length > 1 ? 's' : ''} comparable${avecPrix.length > 1 ? 's' : ''}`
        + (sansTarif ? ` · ${sansTarif} sans tarif déclaré` : '')
        + (p && rouges ? ` · <b>${rouges}</b> au-delà des ressources renseignées` : '')
        + (p ? '' : ` · <b>indiquez ${mot('retraite')}</b> pour estimer le budget`);
    }""",
     """    // Le chiffre de tête répond à la question posée. Sans ressources : combien
    // d'établissements, et leur tarif. Avec : ce qui manquerait chaque mois, ou combien
    // d'établissements sont couverts. (Avant : « 119 établissements » restait en tête,
    // et la réponse se perdait au milieu d'une phrase de cinq lignes.)
    const sansTarif = list.length - avecPrix.length;
    const pl = (k, sg, pr) => (k > 1 ? pr : sg);
    const nEt = (k) => `${nbfr(k)} établissement${k > 1 ? 's' : ''}`;
    const zone = `${nEt(list.length)} à ${s.rayon} km ${esc(de(s.commune.nom))}`
      + (sansTarif ? `, dont ${nbfr(sansTarif)} sans tarif déclaré` : '');
    if (med == null) {
      $('res-titre').textContent = 'Les EHPAD dans cette zone';
      $('res-chiffre').textContent = nEt(list.length);
      $('res-sous').innerHTML = `à ${s.rayon} km ${esc(de(s.commune.nom))} · aucun n’a déclaré son tarif`;
    } else if (!p) {
      $('res-titre').textContent = 'Les EHPAD dans cette zone';
      $('res-chiffre').textContent = nEt(list.length);
      $('res-sous').innerHTML = `Tarif médian ${euro(med)}/mois, de ${euro(mini)} à ${euro(maxi)}, avant les aides.<br>`
        + `<b>Indiquez ${mot('retraite')}</b> pour voir ce qui resterait à payer.<br><small>${zone}</small>`;
    } else {
      const R = ressourcesTotales(s);
      const couverts = avecPrix.filter((o) => !(o.r.trou > 0));
      const manquent = avecPrix.filter((o) => o.r.trou > 0);
      const tMin = manquent.length ? Math.min(...manquent.map((o) => o.r.trou)) : 0;
      const tMax = manquent.length ? Math.max(...manquent.map((o) => o.r.trou)) : 0;
      const ecart = tMin === tMax ? euro(tMin) : `${euro(tMin)} à ${euro(tMax)}`;
      const ref = avecPrix[0].r;
      const tient = manquent.filter((o) => o.r.couleur === 'orange').length;
      const l = [];
      if (!manquent.length) {
        $('res-titre').textContent = `Avec ${euro(R)} de ressources par mois`;
        $('res-chiffre').textContent = `${nEt(couverts.length)} ${pl(couverts.length, 'couvert', 'couverts')}`;
        l.push(`Budget estimé de ${euro(mini)} à ${euro(maxi)}/mois selon l’établissement, aides déduites.`);
      } else if (!couverts.length) {
        $('res-titre').textContent = `Avec ${euro(R)} de ressources par mois, il manquerait chaque mois`;
        $('res-chiffre').textContent = ecart;
        l.push(`Budget estimé de ${euro(mini)} à ${euro(maxi)}/mois selon l’établissement, aides déduites.`);
      } else {
        $('res-titre').textContent = `Avec ${euro(R)} de ressources par mois`;
        $('res-chiffre').textContent = `${nEt(couverts.length)} ${pl(couverts.length, 'couvert', 'couverts')}`;
        l.push(`Pour ${pl(manquent.length, 'l’autre', `les ${nbfr(manquent.length)} autres`)}, il manquerait ${ecart} par mois.`);
      }
      if (tient) l.push(`L’épargne indiquée couvrirait ce manque au moins 5 ans dans ${nEt(tient)}.`);
      l.push(`Calcul fait en laissant ${euro(ref.gardeMini)}/mois pour ${mot('possessif')} dépenses personnelles`
        + ` (10&nbsp;% des ressources, minimum ${euro(BAREME.ashResteMiniEur)})`
        + (ref.reserveConjoint ? ` et ${euro(ref.reserveConjoint)} pour le conjoint à domicile` : '') + '.');
      if (s.gir === '?') l.push('Autonomie non renseignée&nbsp;: calcul sur un GIR 3-4.');
      $('res-sous').innerHTML = l.join('<br>') + `<br><small>${zone}</small>`;
    }
    // mesure du parcours : résultats affichés, puis budget calculé
    if (window.ME_etape) { window.ME_etape('cp'); if (p) window.ME_etape('r'); }
    $('affiner-btn').hidden = !(p && !$('plus-situation').open);"""),

    # P1 — libellé de l'autonomie selon la personne concernée
    ("      'lbl-gir': 'Niveau d’autonomie connu (GIR)',",
     "      'lbl-gir': pourMoi() ? 'Au quotidien, avez-vous besoin d’aide pour…' : 'Au quotidien, votre proche a-t-il besoin d’aide pour…',"),

    # P0/P1 — la mini-grille reste ouverte, et le GIR affiché dit d'où il vient
    ("    $('gir-aide').hidden = state.gir !== '?';", "    majGir();"),
    ("""      state[key] = cast(vals[[...seg.querySelectorAll('button')].indexOf(b)]);
""",
     """      state[key] = cast(vals[[...seg.querySelectorAll('button')].indexOf(b)]);
      // un GIR notifié remplace l'estimation de la mini-grille
      if (key === 'girNotif') { state.gir = state.girNotif; state.girCases = [false, false, false, false, false]; }
"""),
    ("""  $('gir-calc').addEventListener('change', () => {
    const n = [...document.querySelectorAll('#gir-calc input:checked')].length;
    state.gir = n >= 3 ? '12' : n >= 1 ? '34' : '56';
    $('gir-res').textContent = `Estimation indicative : niveau d’autonomie GIR ${state.gir === '12' ? '1-2' : state.gir === '34' ? '3-4' : '5-6'}. Seul le niveau notifié par le département fait foi.`;
    render();
  });""",
     """  $('gir-calc').addEventListener('change', (ev) => {
    const cases = [...document.querySelectorAll('#gir-calc input')];
    const aucun = cases[4];
    // « aucune de ces aides » exclut les autres réponses, et réciproquement
    if (ev.target === aucun && aucun.checked) cases.slice(0, 4).forEach((c) => { c.checked = false; });
    else if (ev.target !== aucun && ev.target.checked) aucun.checked = false;
    state.girCases = cases.map((c) => c.checked);
    state.girNotif = null;
    state.gir = girDeGrille(state.girCases);
    render();
  });
  $('affiner-btn').addEventListener('click', () => {
    const d = $('plus-situation'); d.open = true;
    d.scrollIntoView({ block: 'start', behavior: 'smooth' });
    setTimeout(() => { const f = $('epargne'); if (f) f.focus({ preventScroll: true }); }, 400);
    $('affiner-btn').hidden = true;
  });
  // Mobile : la liste d'abord, la carte sur demande (NN/g 2014 : sur mobile, la carte
  // rallonge les tâches ; aucun utilisateur ne l'a réclamée quand elle était absente).
  $('carte-mob').addEventListener('click', () => {
    const on = !$('atelier').classList.contains('carte-on');
    $('atelier').classList.toggle('carte-on', on);
    $('carte-mob').setAttribute('aria-pressed', String(on));
    $('carte-mob').textContent = on ? 'Masquer la carte' : 'Voir sur la carte';
    if (!on) return;
    evt('map_opened', { source: 'mobile' });
    setTimeout(() => { if (map) { map.invalidateSize(); if (bornesCarte) map.fitBounds(bornesCarte); } }, 60);
    $('pan-carte').scrollIntoView({ block: 'start', behavior: 'smooth' });
  });"""),

    # reprise d'un état enregistré par la version précédente
    ("    state.gir = String(state.gir);   // un état enregistré par une version antérieure pouvait contenir un nombre\n",
     "    state.gir = String(state.gir);   // un état enregistré par une version antérieure pouvait contenir un nombre\n"
     "    if (!Array.isArray(state.girCases) || state.girCases.length !== 5) state.girCases = [false, false, false, false, false];\n"
     "    // Avant ce lot, « GIR 3-4 » était présélectionné : un 3-4 sans grille ni notification n'est\n"
     "    // pas une réponse. Un 1-2 ou un 5-6 l'est : il devient un GIR notifié, visible et modifiable.\n"
     "    if (!state.girNotif && !state.girCases.some(Boolean)) {\n"
     "      if (state.gir === '34') state.gir = '?';\n"
     "      else if (state.gir === '12' || state.gir === '56') state.girNotif = state.gir;\n"
     "    }\n"
     "    if (window.ME_etape) window.ME_etape('a');   // mesure du parcours : arrivée sur l'accueil\n"),

    # tests : le GIR notifié remplace l'ancien sélecteur
    ("""        const seg = document.querySelector('[data-seg^="gir:"]');
        if (!seg) return false;
        const avant = state.gir;
        seg.querySelectorAll('button')[0].click();
        const ok = state.gir === '12' && calcule(E, { ...base, gir: state.gir }).dependance === 21.85 * mois;
        state.gir = avant; majUI();
        return ok;""",
     """        const seg = document.querySelector('[data-seg^="girNotif:"]');
        if (!seg) return false;
        const avant = state.gir, avantN = state.girNotif, avantC = state.girCases;
        seg.querySelectorAll('button')[0].click();
        const ok = state.gir === '12' && state.girNotif === '12'
          && calcule(E, { ...base, gir: state.gir }).dependance === 21.85 * mois;
        state.gir = avant; state.girNotif = avantN; state.girCases = avantC; majUI();
        return ok;
      }],
      ['Mini-grille : 3 aides → GIR 1-2, 1 aide → 3-4, « aucune » → 5-6, rien → inconnu', () =>
        girDeGrille([true, true, true, false, false]) === '12' && girDeGrille([false, true, false, false, false]) === '34'
        && girDeGrille([false, false, false, false, true]) === '56' && girDeGrille([false, false, false, false, false]) === '?'],
      ['Noms lisibles : formule générique collée au nom (FINESS 690785662)', () =>
        nomLisible('ETABLISSEMENT POUR PERSONNES ÂGEES DÉPENDANTESLOUISE-THÉRÈSE', 'ECULLY') === 'EHPAD Louise-Thérèse'
        && nomLisible("ETABLISSEMENT D'HEBERGEMENT POUR PERSONNES AGEES DEPENDANTES", 'BRUAY LA BUISSIERE CEDEX') === 'EHPAD de Bruay La Buissiere'
        && nomLisible('EHPAD LES TILLEULS MONTLUEL', 'MONTLUEL') === 'EHPAD Les Tilleuls Montluel'],
      ['Ce qui manque laisse 10 % des ressources (au moins 125 €) à la personne', () => {
        const r = calcule(E, { ...base, revenus: 1500 });
        const r2 = calcule(E, { ...base, revenus: 1000 });
        return r.gardeMini === 150 && Math.abs(r.trou - Math.max(0, r.decaisse - 1350)) < 0.01
          && r2.gardeMini === 125;"""),
])

# « Distance » a quitté le formulaire : ses trois écritures deviennent conditionnelles
p = os.path.join(B, APP)
s = io.open(p, encoding='utf-8').read()
a = "$('rayon').value = String(state.rayon);"
k = s.count(a)
if k != 3 and "if ($('rayon')) $('rayon').value" not in s:
    print('rayon : %d occurrences au lieu de 3' % k); sys.exit(1)
s = s.replace("if ($('rayon')) " + a, a).replace(a, "if ($('rayon')) " + a)
# fonctions ajoutées, posées avant majPourQui
AJOUT = """  /** Mini-grille d'autonomie → GIR estimé. Trois aides ou plus : 1-2 ; une ou deux : 3-4 ;
      « aucune de ces aides » : 5-6 ; aucune réponse : inconnu (« ? »), calcul sur 3-4, affiché. */
  function girDeGrille(c) {
    const k = (c || []).slice(0, 4).filter(Boolean).length;
    return k >= 3 ? '12' : k >= 1 ? '34' : (c && c[4]) ? '56' : '?';
  }
  const LIB_GIR = { '12': 'GIR 1-2', '34': 'GIR 3-4', '56': 'GIR 5-6' };
  /** Recoche la grille d'après l'état, et dit d'où vient le GIR retenu. */
  function majGir() {
    const c = Array.isArray(state.girCases) ? state.girCases : [];
    document.querySelectorAll('#gir-calc input').forEach((x, i) => { x.checked = !!c[i]; });
    const r = $('gir-res'); if (!r) return;
    r.textContent = state.girNotif ? `GIR notifié retenu : ${LIB_GIR[state.girNotif]}.`
      : state.gir === '?' ? 'Sans réponse, le calcul retient un niveau intermédiaire (GIR 3-4) et le signale.'
      : `Estimation indicative : ${LIB_GIR[state.gir]}. Seul le niveau notifié par le département fait foi.`;
    const d = $('gir-notif'); if (d && state.girNotif) d.open = true;
  }

  /** Réécrit les libellés de la page selon la personne concernée. Aucun calcul n'en dépend. */"""
m = "  /** Réécrit les libellés de la page selon la personne concernée. Aucun calcul n'en dépend. */"
if 'function girDeGrille' not in s:
    if s.count(m) != 1: print('ancre majPourQui introuvable'); sys.exit(1)
    s = s.replace(m, AJOUT, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('patch_ux_accueil (application) : terminé,', n, 'remplacements au total')
