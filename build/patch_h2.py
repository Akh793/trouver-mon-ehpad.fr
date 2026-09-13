# -*- coding: utf-8 -*-
"""Les titres perdaient l'espace entre leurs mots.

`h2` était en `display:flex` pour aligner la pastille numérotée avec le texte.
Or un conteneur flex transforme chaque nœud en item séparé : dans
« Parcourir <em>sans calculer</em> », le texte nu « Parcourir » et le `<em>`
deviennent deux items, et l'espace qui les séparait dans le HTML est supprimé —
d'où « Parcourirsans calculer ». Le `gap:0` posé en v2.4 pour empêcher l'espacement
de s'ajouter AUTOUR du texte a rendu le défaut systématique sur tous les titres
contenant une mise en valeur.

Le titre redevient un bloc de texte ordinaire, où les espaces comptent. Seule la
pastille est alignée, par `display:inline-flex` sur elle-même : c'est le seul
élément qui avait besoin du flex, pas le titre entier.
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
    "h2{font-size:clamp(1.5rem,3.4vw,2.25rem);display:flex;align-items:center;gap:0;flex-wrap:wrap}",
    """/* Pas de flex ici : il ferait de chaque nœud un item et supprimerait les espaces
   entre le texte nu et les <em> — « Parcourirsans calculer ». */
h2{font-size:clamp(1.5rem,3.4vw,2.25rem);line-height:1.2}"""
)
rem(
    "h2 .n{width:2.4rem;height:2.4rem;margin-right:.7rem;flex:0 0 auto;border-radius:999px;background:var(--bl);color:#fff;display:grid;place-items:center;font-size:1.05rem}",
    """/* La pastille s'aligne seule sur la ligne de texte : elle est le seul élément qui
   demandait un alignement, pas le titre entier. */
h2 .n{width:2.4rem;height:2.4rem;margin-right:.7rem;border-radius:999px;background:var(--bl);color:#fff;
  display:inline-flex;align-items:center;justify-content:center;font-size:1.05rem;vertical-align:-.55rem}"""
)

io.open(P, 'w', encoding='utf-8').write(s)
print('%d blocs posés' % n)
