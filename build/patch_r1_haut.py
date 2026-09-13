# -*- coding: utf-8 -*-
"""Refonte rédactionnelle — lot 1 : haut de page.

Le titre promettait un prix « vraiment » exact, répété dans le chapô (« paierez
vraiment »), puis dans les résultats (« reste à charge réel »). Une estimation ne
peut pas tenir cette promesse : elle dépend de données déclaratives et de décisions
départementales. Le titre dit désormais ce que le service fait.

Le temps de calcul en millisecondes s'adressait au développeur. La date de
vérification des règles quitte l'en-tête : elle dit que les BARÈMES sont à jour, pas
que les tarifs le sont — elle appartient aux sources.
"""
import io, os, sys

B = os.path.dirname(os.path.abspath(__file__))
n = 0


def patch(rel, paires):
    global n
    p = os.path.join(B, rel)
    s = io.open(p, encoding='utf-8').read()
    for a, b in paires:
        if a not in s:
            print('INTROUVABLE dans %s :' % rel, a[:110].replace('\n', ' '))
            sys.exit(1)
        s = s.replace(a, b, 1)
        n += 1
    io.open(p, 'w', encoding='utf-8').write(s)


patch('index.template.html', [
    # ── Titre et présentation
    ("""        <h1 id="h1-titre">Ce que l’EHPAD coûtera<br><span class="h1-l2"><em class="bl">vraiment</em> à <em class="co">votre parent</em></span></h1>""",
     """        <h1 id="h1-titre">Trouvez un EHPAD<br><span class="h1-l2">et <em class="bl">estimez</em> son <em class="co">coût</em></span></h1>"""),

    ("""    <p class="sub">Découvrez ce que vous paierez vraiment en EHPAD.<br><span class="sub2">Renseignez la situation de votre parent et comparez, établissement par établissement, le reste à charge après aides.</span></p>""",
     """    <p class="sub">Comparez les établissements dans la zone de votre choix.<br><span class="sub2">Précisez votre situation pour estimer votre budget mensuel. Gratuit, sans inscription.</span></p>"""),

    # ── L'en-tête se allège : le temps de calcul et la date des barèmes s'en vont
    ("""        <span class="badge b-coral">Règles à jour au&nbsp;<span class="meta-date">—</span></span>
        <span class="perf">temps de calcul : <span id="perf">—</span></span>""",
     """"""),

    # ── Le choix de personne : sans l'explication inutile
    ("""        <label>Pour qui faites-vous cette recherche&nbsp;?</label>
        <div class="seg" data-seg="pourQui:proche,moi" role="group" aria-label="Pour qui">
          <button type="button">Un proche</button><button type="button">Moi-même</button>
        </div>
        <p class="fld-h">Cela ne change rien au calcul, seulement la façon dont les questions sont posées.</p>""",
     """        <label>Vous cherchez pour…</label>
        <div class="seg" data-seg="pourQui:proche,moi" role="group" aria-label="Vous cherchez pour">
          <button type="button">Un proche</button><button type="button">Moi-même</button>
        </div>"""),

    # ── L'entrée dans la recherche
    ("""        <label for="cp">Où chercher</label>""",
     """        <label for="cp">Code postal recherché</label>"""),
    ("""        <p id="cp-aide" class="fld-h">Le code postal de la famille, pas celui du parent : c’est la distance de visite qui compte.</p>""",
     """        <p id="cp-aide" class="fld-h">La zone où vous cherchez un établissement.</p>"""),
    ("""        <label for="rayon">Dans un rayon de</label>""",
     """        <label for="rayon">Distance autour de ce lieu</label>"""),
    ("""        <p class="fld-h">Au-delà de 40 résultats, la carte regroupe les établissements.</p>""",
     """        <p class="fld-h">Distance à vol d’oiseau, pas par la route.</p>"""),

    # ── Le titre de bande : « Estimer le budget »
    ("""      <h2><span class="n">1</span> <span id="lbl-situation">La situation de votre parent</span></h2>""",
     """      <h2><span class="n">1</span> <span id="lbl-situation">Estimer le budget</span></h2>"""),
])

patch(os.path.join('..', 'site', 'app.js'), [
    # ── Le titre ne dépend plus de la personne concernée : il est neutre et stable
    ("""    // Le titre change de tournure, pas seulement de mot : « coûtera vraiment à vous »
    // ne se dit pas. Deux phrases complètes, chacune correcte.
    const h1 = $('h1-titre');
    if (h1) {
      h1.innerHTML = pourMoi()
        ? 'Ce que l’EHPAD vous coûtera<br><span class="h1-l2"><em class="bl">vraiment</em>, <em class="co">chaque mois</em></span>'
        : 'Ce que l’EHPAD coûtera<br><span class="h1-l2"><em class="bl">vraiment</em> à <em class="co">votre parent</em></span>';
    }
    const t = {
      'lbl-revenus'""",
     """    // Le titre est neutre : il n'a plus à être réécrit selon la personne concernée.
    const t = {
      'lbl-revenus'"""),

    ("""      'lbl-situation': pourMoi() ? 'Votre situation' : 'La situation de votre parent',
      'nav-situation': pourMoi() ? 'Votre situation' : 'La situation de votre parent',""",
     """      'lbl-situation': 'Estimer le budget',
      'nav-situation': 'Estimer le budget',"""),

    ("""      'lbl-revenus': pourMoi() ? 'Vos retraites et pensions' : 'Retraites et pensions du parent',""",
     """      'lbl-revenus': pourMoi() ? 'Vos retraites et pensions par mois' : 'Retraites et pensions du proche, par mois',"""),

    ("""      'lbl-gir': pourMoi() ? 'Votre niveau de dépendance (GIR)' : 'Niveau de dépendance (GIR)',""",
     """      'lbl-gir': 'Niveau d’autonomie connu (GIR)',"""),

    ("""      'lbl-couple': pourMoi() ? 'Vivez-vous en couple ?' : 'Vit-il ou elle en couple ?',
      'lbl-proprio': pourMoi() ? 'Êtes-vous propriétaire de votre logement ?' : 'Est-il ou elle propriétaire de son logement ?',""",
     """      'lbl-couple': pourMoi() ? 'Vivez-vous en couple ?' : 'Vit-il ou elle en couple ?',
      'lbl-proprio': pourMoi() ? 'Êtes-vous propriétaire de votre logement ?' : 'Est-il ou elle propriétaire de son logement ?',
      'lbl-impot': pourMoi() ? 'Payez-vous l’impôt sur le revenu ?' : 'Paie-t-il ou elle l’impôt sur le revenu ?',
      'lbl-enfants': 'Simuler une participation des enfants',"""),

    ("""    const v = $('v-s');
    if (v) v.textContent = 'Les établissements autour de vous s’affichent aussitôt. Indiquez ensuite '
      + (pourMoi() ? 'votre retraite' : 'la retraite de votre parent')
      + ' : chaque tarif devient le montant qui resterait réellement à payer.';""",
     """    const v = $('v-s');
    if (v) v.textContent = 'Les établissements s’affichent aussitôt, avec leur tarif. '
      + 'Précisez ensuite votre situation pour estimer le budget mensuel.';"""),
])

print('%d blocs posés' % n)
