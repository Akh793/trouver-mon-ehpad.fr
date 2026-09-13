# -*- coding: utf-8 -*-
"""Les 6 778 fiches d'établissement ignoraient le régime de financement.

Pour les 1 617 établissements des territoires d'expérimentation, elles présentaient
la participation forfaitaire comme un « tarif dépendance » qui varierait selon le
GIR, et annonçaient une APA « qui en couvre une grande partie » alors qu'elle y est
supprimée. Le régime est désormais chargé avec les lignes et conditionne le texte.
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


# ── 1. Le régime est calculé au chargement, par la même source que le site
patch('seo/base.py', [
    ("""def charge():
    rows = json.load(open(os.path.join(B, 'merged_v2.json'), encoding='utf-8'))""",
     """def charge():
    rows = json.load(open(os.path.join(B, 'merged_v2.json'), encoding='utf-8'))
    # Régime de financement de la dépendance, déduit du territoire d'implantation par
    # le même module que les données servies au calculateur : les pages et le moteur
    # ne peuvent donc pas diverger.
    import sys as _sys
    if B not in _sys.path:
        _sys.path.insert(0, B)
    import regime as _regime
    _R = _regime.Regimes()
    _PF = _R.participation()"""),
    ("""        r['serie'] = serie_calculee(serie.get(r['fin']))
    return rows, communes""",
     """        r['serie'] = serie_calculee(serie.get(r['fin']))
        r['reg'] = _R.pour(insee=r.get('insee'), cp=r.get('cp'))
        r['pf'] = _PF
    return rows, communes"""),
])

# ── 2. La fiche : le bloc de tarifs distingue les deux régimes
patch('seo/fiches.py', [
    ("""    if r['t12'] and r['t56'] and abs(r['t12'] - r['t56']) > 0.01:""",
     """    if r.get('reg') == 'exp':
        pf = r.get('pf') or {}
        l.append('<li><b>Aide au quotidien&nbsp;: participation forfaitaire</b> de '
                 f'{eur2(pf.get("montant", 0))} par jour, soit environ {eur(mois_eur(pf.get("montant", 0)))} par mois. '
                 'Cette commune fait partie des territoires qui expérimentent, depuis le 1<sup>er</sup> juillet 2025, '
                 'la fusion des financements soins et dépendance&nbsp;: il n’y a plus de tarif par GIR, plus de '
                 'participation qui augmente avec les ressources, et l’allocation personnalisée d’autonomie en '
                 'établissement y est supprimée. Le montant est le même pour tous les résidents.</li>')
    elif r['t12'] and r['t56'] and abs(r['t12'] - r['t56']) > 0.01:"""),
    ("""<p>Dans tous les cas, trois aides viennent réduire la facture avant l’aide sociale&nbsp;: <a href="/aides-ehpad/apa/">l’allocation personnalisée d’autonomie</a>, qui couvre une grande partie du tarif dépendance ; <a href="/aides-ehpad/aide-au-logement/">l’aide au logement</a>, si l’établissement est conventionné ; et <a href="/aides-ehpad/reduction-impot/">la réduction d’impôt</a> de 25 % des frais restants, si la personne est imposable.</p></section>""",
     """<p>{"Ici, l’allocation personnalisée d’autonomie en établissement est supprimée : la participation forfaitaire en tient lieu. Reste " if r.get('reg') == 'exp' else "Avant l’aide sociale, deux aides réduisent la facture : " }<a href="/aides-ehpad/apa/">{"" if r.get('reg') == 'exp' else "l’allocation personnalisée d’autonomie, qui couvre une grande partie du tarif dépendance"}</a>{"" if r.get('reg') == 'exp' else " ; "}<a href="/aides-ehpad/aide-au-logement/">l’aide au logement</a>, si l’établissement est conventionné. <a href="/aides-ehpad/reduction-impot/">La réduction d’impôt</a> de 25 % des frais restants, elle, n’arrive que l’année suivante et seulement si la personne paie de l’impôt : elle n’allège aucune mensualité.</p></section>"""),
])

print('%d blocs corrigés' % n)
