# -*- coding: utf-8 -*-
"""Rattache /retours/ au reste du site : pied de page, sitemap, mentions légales.

Une page qu'aucun lien n'atteint n'existe pas. Et une page qui reçoit des messages
doit apparaître dans les mentions légales : sans elle, le site affirme ne rien
collecter, ce qui cesse d'être vrai.
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
    ("""      <a href="mailto:contact@trouver-mon-ehpad.fr?subject=Mon%20EHPAD%20%E2%80%94%20contact">Nous écrire</a>""",
     """      <a href="/retours/">Vos retours</a>
      <a href="mailto:contact@trouver-mon-ehpad.fr?subject=Mon%20EHPAD%20%E2%80%94%20contact">Nous écrire</a>"""),
])

patch(os.path.join('seo', 'build_seo.py'), [
    ("""    groupes['pages'] += [('/', 1.0), ('/notre-methodologie.html', 0.6),
                         ('/qui-sommes-nous.html', 0.4)]""",
     """    groupes['pages'] += [('/', 1.0), ('/notre-methodologie.html', 0.6),
                         ('/qui-sommes-nous.html', 0.4), ('/retours/', 0.4)]"""),
])

print('%d blocs posés' % n)
