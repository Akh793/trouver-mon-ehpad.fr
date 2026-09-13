# -*- coding: utf-8 -*-
"""Les anomalies détectées par les contrôles doivent se voir dans le produit,
pas seulement dans un rapport de build.

Trois cas :
  1. tarifs GIR dans un ordre impossible → le calcul de dépendance devient douteux ;
  2. évaluation HAS datée dans le futur → ce n'est pas un résultat, c'est une visite prévue ;
  3. couverture des données → chiffres recalculés à chaque build, affichés tels quels.
"""
import io, os, sys

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site', 'app.js')
s = io.open(P, encoding='utf-8').read()
n = 0


def rem(a, b):
    global s, n
    if a not in s:
        print('INTROUVABLE :', a[:110].replace('\n', ' '))
        sys.exit(1)
    s = s.replace(a, b, 1)
    n += 1


# ── 1. Ordre des tarifs GIR
rem(
    """        if (Math.abs(tg - t56) < 0.01) {
          notes.push('Cet établissement déclare le même tarif quel que soit le niveau d’autonomie, '
            + 'alors qu’il relève du régime de droit commun. L’aide du département ressort donc à zéro ici. '
            + 'Demandez-lui le tarif qui s’appliquera réellement.');
        }""",
    """        if (Math.abs(tg - t56) < 0.01) {
          notes.push('Cet établissement déclare le même tarif quel que soit le niveau d’autonomie, '
            + 'alors qu’il relève du régime de droit commun. L’aide du département ressort donc à zéro ici. '
            + 'Demandez-lui le tarif qui s’appliquera réellement.');
        }
        // Le barème impose t12 ≥ t34 ≥ t56. Un ordre inverse signale une déclaration
        // erronée : le montant calculé ici ne peut pas être tenu pour fiable.
        const t12 = e[C.t12], t34 = e[C.t34];
        if (t12 != null && t34 != null && (t12 < t34 - 0.001 || t34 < t56 - 0.001)) {
          depDouteuse = true;
          notes.push('Les tarifs dépendance déclarés par cet établissement sont dans un ordre impossible '
            + '(' + euro2(t12) + ' / ' + euro2(t34) + ' / ' + euro2(t56) + ' par jour du GIR 1-2 au GIR 5-6, '
            + 'alors que le tarif décroît toujours avec le niveau de dépendance). '
            + 'La part « aide au quotidien » affichée ici n’est donc pas fiable : faites-la confirmer.');
        }"""
)
rem(
    "    let dependance = 0, apa = 0, apaConnue = false, pfJour = null, depConnue = false;",
    "    let dependance = 0, apa = 0, apaConnue = false, pfJour = null, depConnue = false, depDouteuse = false;"
)
rem(
    "      prixConnu: true, pj, nbRes, reg, pfJour, depConnue,",
    "      prixConnu: true, pj, nbRes, reg, pfJour, depConnue, depDouteuse,"
)

# ── 2. Évaluation HAS datée dans le futur
rem(
    """    if (!e[C.hasN]) return '<span class="badge b-gris">qualité non évaluée</span>';""",
    """    if (e[C.hasD] && String(e[C.hasD]).slice(0, 10) > new Date().toISOString().slice(0, 10)) {
      return '<span class="badge b-gris">évaluation à venir</span>';
    }
    if (!e[C.hasN]) return '<span class="badge b-gris">qualité non évaluée</span>';"""
)
rem(
    """      return `<div class="ln"><span>Évaluation officielle</span><b>${e[C.hasN] || 'non publiée'}</b></div>""",
    """      const hasFutur = e[C.hasD] && String(e[C.hasD]).slice(0, 10) > new Date().toISOString().slice(0, 10);
      return `${hasFutur ? `<p class="warn">La date d’évaluation publiée par la Haute Autorité de santé
          (${dfr(e[C.hasD])}) est postérieure à aujourd’hui. Il s’agit d’une visite programmée, ou d’une
          erreur de saisie à la source&nbsp;: le résultat ci-dessous ne peut pas être lu comme une
          évaluation déjà rendue.</p>` : ''}
        <div class="ln"><span>Évaluation officielle</span><b>${e[C.hasN] || 'non publiée'}</b></div>"""
)

io.open(P, 'w', encoding='utf-8').write(s)
print('%d blocs posés' % n)
