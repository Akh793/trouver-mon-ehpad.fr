# -*- coding: utf-8 -*-
"""Alignement de l'affichage sur le nouveau modèle de résultat.

`r.total` reste valide (= r.facture). Disparaissent : `r.ir` (l'avantage fiscal n'est plus
mensuel) et `r.dispoEst` (les places libres extrapolées).
"""
import io, os, sys

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site', 'app.js')
s = io.open(P, encoding='utf-8').read()
n = 0


def rem(a, b, obligatoire=True):
    global s, n
    if a not in s:
        if obligatoire:
            print('INTROUVABLE :', a[:110].replace('\n', ' '))
            sys.exit(1)
        return False
    s = s.replace(a, b, 1)
    n += 1
    return True


# ── 1. Le tri « places libres estimées » disparaît
rem(
    "      if (k === 'marge') return (b.r.dispoEst?.libres100 ?? -1) - (a.r.dispoEst?.libres100 ?? -1) || a.dist - b.dist;",
    "      // le tri « places libres estimées » a été retiré : aucune source ne donne la disponibilité réelle"
)
rem(
    "    if (s.tri === 'marge' && o.r.dispoEst) raisons.push('le segment où les places se libèrent le plus souvent');",
    "",
)

# ── 2. L'onglet Essentiel : plus de places extrapolées, mais le régime et la fraîcheur
rem(
    "    if (r.dispoEst) l.push(`<div class=\"ln\"><span>Places qui se libèrent chaque année, sur 100</span><b>${nbfr(r.dispoEst.libres100)}</b></div>`);",
    """    l.push(`<div class="ln"><span>Aide au quotidien</span><b>${r.reg === 'exp'
      ? 'forfait de ' + euro2(r.pfJour) + '/jour'
      : r.reg === 'inconnu' ? 'régime à confirmer' : 'selon le niveau d’autonomie'}</b></div>`);
    l.push('<p class="f-note">Disponibilité&nbsp;: aucune source publique ne donne les places libres d’un établissement. '
      + 'À demander directement.</p>');"""
)

# ── 3. Le comparateur : on retire la colonne extrapolée
rem(
    "    ['libres', 'Places libres pour 100 (segment)', (o) => (o.r.dispoEst ? nbfr(o.r.dispoEst.libres100) : 'information non disponible')],",
    "    ['reg', 'Aide au quotidien', (o) => (o.r.reg === 'exp' ? 'forfait ' + euro2(o.r.pfJour) + '/jour' : o.r.reg === 'inconnu' ? 'régime à confirmer' : 'selon le GIR')],"
)

# ── 4. L'export CSV : plus de colonnes extrapolées
rem(
    "      o.r.dispoEst ? o.r.dispoEst.occ : '', o.r.dispoEst && o.r.dispoEst.jours ? o.r.dispoEst.jours : '']);",
    "      o.r.secteur ? o.r.secteur.occ : '', o.r.reg]);"
)

# ── 5. Le détail des aides : la réduction d'impôt sort du mensuel
rem(
    """    if (r.ir > 0) aides.push([
      'La réduction d’impôt', r.ir,
      `25 % des frais, jusqu’à ${euro(BAREME.irPlafond * r.nbRes)} par an. Elle arrive l’année suivante, pas chaque mois — ici elle est ramenée au mois pour comparer.`]);""",
    ""
)

# ── 6. Le bloc de détail se termine sur le décaissement, puis l'avantage fiscal à part
rem(
    """    h += l('<b>Ce qu’il reste à payer</b>', '<b>' + euro(r.rac) + '/mois</b>', 'tot');
    h += `<p class="f-note">C’est ce que votre parent, et au besoin sa famille, devront financer
      chaque mois sur leurs ressources et leur épargne.</p>`;
    return h;""",
    """    h += l('<b>Ce qu’il faut sortir chaque mois</b>', '<b>' + euro(r.decaisse) + '/mois</b>', 'tot');
    h += `<p class="f-note">C’est la somme à décaisser, une fois les aides versées à
      l’établissement déduites. Ni l’impôt, ni l’aide sociale ne sont comptés ici.</p>`;

    // L'avantage fiscal : annuel, différé, conditionnel — donc présenté à part.
    if (r.fisc && r.fisc.applicable && r.fisc.reduction > 0) {
      h += '<h4 class="f-t1">Et l’année suivante, l’impôt</h4>';
      h += l('Réduction d’impôt, au maximum', euro(r.fisc.reduction) + '/an');
      h += `<p class="f-note">25&nbsp;% des frais restants, dans la limite de
        ${euro(r.fisc.plafondDepenses)} de dépenses${r.fisc.moisRetenus < 12
          ? ' pour ' + r.fisc.moisRetenus + ' mois de séjour' : ' par an'}${r.nbRes > 1 ? ' et par personne hébergée' : ''}.
        ${r.fisc.plafonne ? 'Les frais dépassent ce plafond&nbsp;: le surplus ne donne droit à rien. ' : ''}
        C’est un <b>maximum</b>&nbsp;: une réduction d’impôt ne peut pas dépasser l’impôt réellement dû,
        et elle n’est pas remboursée. Elle arrive l’année suivante, jamais chaque mois.</p>`;
    } else if (r.fisc && !r.fisc.applicable) {
      h += `<p class="f-note">Une réduction d’impôt de 25&nbsp;% existe pour les personnes imposables.
        Indiquez-le dans «&nbsp;Préciser la situation&nbsp;» pour voir ce qu’elle représenterait.</p>`;
    }
    return h;"""
)

io.open(P, 'w', encoding='utf-8').write(s)
print('%d blocs alignés' % n)
