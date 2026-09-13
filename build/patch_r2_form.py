# -*- coding: utf-8 -*-
"""Refonte rédactionnelle — lot 2 : le formulaire.

Un défaut de fond d'abord. Le texte sous « Qu'est-ce qui compte le plus pour vous ? »
affirmait : « Ce choix change l'ordre des résultats, JAMAIS LEUR CONTENU. » C'était
faux. `normalise()` transformait la priorité « Les aides » en filtre : besoinAsh
passait à « oui » et ashOnly à vrai, faisant disparaître de la liste tous les
établissements non habilités — sans que rien ne le dise.

Le choix redevient ce qu'il annonce : un ordre. Le filtre sur l'aide sociale garde
son propre contrôle, explicite, avec sa pastille de retrait. Un établissement ne
disparaît plus à cause d'un réglage présenté comme un tri.

Le reste du lot ramène les aides sous les champs à une phrase. Les règles complètes
— seuils, plafonds, barèmes — quittent le formulaire : leur place est près du
résultat qu'elles expliquent, pas au-dessus d'un champ vide.
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


patch(os.path.join('..', 'site', 'app.js'), [
    ("""    state.ashOnly = state.besoinAsh === 'oui';
    if (state.priorite === 'ash') { state.tri = 'rac'; state.besoinAsh = 'oui'; state.ashOnly = true; }
    else if (state.priorite) state.tri = state.priorite;""",
     """    // Le filtre sur l'aide sociale a son propre contrôle, et lui seul.
    state.ashOnly = state.besoinAsh === 'oui';
    // La priorité ordonne, elle ne retire rien : elle annonçait un tri et posait un
    // filtre, de sorte que des établissements disparaissaient sans explication.
    if (state.priorite) state.tri = state.priorite;"""),

    # le tri « aides » remonte les établissements habilités sans masquer les autres
    ("""      if (k === 'has') { const o = { A: 0, B: 1, C: 2, D: 3 }; return (o[a.e[C.hasN]] ?? 9) - (o[b.e[C.hasN]] ?? 9) || a.dist - b.dist; }""",
     """      if (k === 'has') { const o = { A: 0, B: 1, C: 2, D: 3 }; return (o[a.e[C.hasN]] ?? 9) - (o[b.e[C.hasN]] ?? 9) || a.dist - b.dist; }
      // « Les aides » remonte les établissements habilités à l'aide sociale, puis
      // départage par reste à charge. Aucun établissement n'est retiré de la liste.
      if (k === 'ash') {
        const o = (x) => (x.e[C.ash] === 1 ? 0 : x.e[C.ash] === 2 ? 1 : 2);
        return o(a) - o(b) || (a.r.rac ?? 1e9) - (b.r.rac ?? 1e9);
      }"""),
])

patch('index.template.html', [
    ("""      <p class="fld-h">Ce choix change l’ordre des résultats, jamais leur contenu. Vous pouvez en changer à tout moment.</p>""",
     """      <p class="fld-h">Change l’ordre des résultats, pas la liste.</p>"""),

    # ── Les aides sous les champs : une phrase, la règle part vers le résultat
    ("""        <p class="fld-h">Le GIR est notifié par le département. Il fixe le tarif dépendance facturé.</p>""",
     """        <p class="fld-h">Si un GIR a déjà été attribué, indiquez-le ici.</p>"""),
    ("""        <p class="fld-h">Un seul chiffre rond. C’est l’entrée de l’APA et de l’aide sociale.</p>""",
     """        <p class="fld-h">Montant mensuel perçu, toutes pensions confondues.</p>"""),
    ("""        <p class="fld-h">Loyers perçus, rente viagère, revenus de placements. Le département les compte dans l’aide sociale ; l’APA aussi.</p>""",
     """        <p class="fld-h">Loyers, rentes ou revenus de placements.</p>"""),
    ("""        <p class="fld-h">Sert à savoir combien de mois l’épargne tient face au reste à charge.</p>""",
     """        <p class="fld-h">Pour estimer combien de temps elle peut compléter le budget.</p>"""),
    ("""        <p class="fld-h">Nous ne l’inventons pas : elle dépend du conventionnement de l’établissement. Demandez-la, puis saisissez-la ici.</p>""",
     """        <p class="fld-h">Le montant notifié, pour l’établissement concerné.</p>"""),
    ("""        <p class="fld-h">La chambre double est facturée au tarif « chambre double » déclaré par l’établissement, quand il en déclare un.</p>""",
     """        <p class="fld-h">Le tarif d’une chambre double vaut pour une personne.</p>"""),
    ("""        <p class="fld-h">Si oui, la réduction d’impôt de 25 % est déduite (plafond 2 500 € par an et par personne hébergée).</p>""",
     """        <p class="fld-h">L’effet fiscal est détaillé dans la fiche, à part du budget mensuel.</p>"""),
    ("""        <p class="fld-h">En couple, le barème de l’APA retient les ressources du ménage divisées par deux. Indiquez celles du conjoint ci-dessous.</p>""",
     """        <p class="fld-h">Le barème de l’APA retient les ressources du ménage.</p>"""),
    ("""        <p class="fld-h">Change le scénario aide sociale : le département récupère sur la succession.</p>""",
     """        <p class="fld-h">Utilisé pour le scénario d’aide sociale.</p>"""),
    ("""        <p class="fld-h">Laissez «&nbsp;Aucun&nbsp;» si vous ne souhaitez pas ce calcul. Le site répartit à parts égales ce qui n’est pas couvert&nbsp;: aucun barème national n’existe, le département ou le juge tranche.</p>""",
     """        <p class="fld-h">Partage égal proposé, sans valeur de décision officielle.</p>"""),
    ("""        <p class="fld-h">À saisir à part : le barème de l’APA divise par deux les ressources <b>du couple</b>, pas celles du résident seul. Sans ce chiffre, l’aide calculée est trop élevée.</p>""",
     """        <p class="fld-h">Sans ce montant, l’aide calculée serait trop élevée.</p>"""),

    # ── Libellés : le sujet avant la règle
    ("""        <label for="autres">Autres revenus mensuels</label>""",
     """        <label for="autres">Autres revenus par mois</label>"""),
    ("""        <label for="apl">Aide au logement déjà notifiée</label>""",
     """        <label for="apl">Aide au logement accordée pour cet EHPAD</label>"""),
    ("""        <label>Chambre</label>""",
     """        <label>Type de chambre</label>"""),
    ("""        <label>Le parent paie-t-il de l’impôt sur le revenu ?</label>""",
     """        <label id="lbl-impot">Paie-t-il ou elle l’impôt sur le revenu&nbsp;?</label>"""),
    ("""        <label for="enfants">Combien d’enfants peuvent participer ?</label>""",
     """        <label for="enfants" id="lbl-enfants">Simuler une participation des enfants</label>"""),
    ("""        <label for="revconj">Retraites et pensions du conjoint</label>""",
     """        <label for="revconj">Retraites et pensions du conjoint, par mois</label>"""),
    ("""      <summary><b>Préciser la situation</b> <span>— épargne, couple, enfants, impôt : le calcul devient plus juste</span></summary>""",
     """      <summary><b>Préciser ma situation</b> <span>— facultatif : revenus, couple, aides, participation familiale</span></summary>"""),
])

print('%d blocs posés' % n)
