# -*- coding: utf-8 -*-
"""Les contrôles d'une même ligne ne démarraient pas à la même hauteur.

Un libellé sur deux lignes — « Le parent paie-t-il de l'impôt sur le revenu ? » —
repoussait son bouton vers le bas, tandis que « Vivez-vous en couple ? », sur une
seule ligne, laissait le sien plus haut. L'œil lisait une rangée en escalier.

Le libellé réserve désormais deux lignes dans toutes les cellules. Mesure faite
avant de choisir cette valeur : à 1 440, 1 280, 1 100, 900 et 700 px, aucun libellé
des deux grilles ne dépasse deux lignes. Le cas à trois lignes n'existe pas, donc
la réserve suffit partout et l'alignement ne peut pas se rompre à une largeur
intermédiaire.
"""
import io, os, sys

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site.css')
s = io.open(P, encoding='utf-8').read()
n = 0


def rem(a, b):
    global s, n
    if a not in s:
        print('INTROUVABLE :', a[:110].replace('\n', ' '))
        sys.exit(1)
    s = s.replace(a, b, 1)
    n += 1


rem(
    ".grid4 .fld label,.grid3 .fld label{color:var(--ink);font-size:.88rem}",
    """.grid4 .fld label,.grid3 .fld label{color:var(--ink);font-size:.88rem;
  /* deux lignes réservées : sans elles, un libellé long décale son champ vers le
     bas et la rangée se lit en escalier. Aucun libellé ne dépasse deux lignes
     entre 700 et 1 440 px — la réserve couvre donc toutes les largeurs. */
  line-height:1.25;min-height:2.5em;display:flex;align-items:flex-start}"""
)

io.open(P, 'w', encoding='utf-8').write(s)
print('%d bloc posé' % n)
