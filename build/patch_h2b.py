# -*- coding: utf-8 -*-
"""Titres numérotés : la pastille s'aligne, et le texte reste indenté sur plusieurs lignes.

Ma correction précédente avait retiré le flex du `h2` pour rendre les espaces entre
mots — ce qu'elle a fait — mais elle laissait deux défauts :

  1. la pastille était calée par un `vertical-align:-.55rem` fixe, alors que la
     taille du titre varie avec la largeur (`clamp`). Un décalage en rem ne peut pas
     suivre une police variable : l'alignement n'était juste qu'à une seule largeur ;
  2. sur un écran étroit, le titre passe à la ligne. La deuxième ligne repartait
     sous la pastille au lieu de s'aligner sur le texte de la première.

Une grille à deux colonnes règle les deux : la pastille occupe la première, tout le
texte la seconde. Le texte formant une seule cellule, ses espaces internes sont
préservés — ce que le flex détruisait en faisant de chaque nœud un item séparé.
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


# ── Le texte du titre devient un bloc unique : c'est lui qui portera la colonne
patch('index.template.html', [
    ("""      <h2><span class="n">1</span> <span id="lbl-situation">Estimer le budget</span></h2>""",
     """      <h2><span class="n">1</span><span class="t" id="lbl-situation">Estimer le budget</span></h2>"""),
    ("""    <h2><span class="n">2</span> Comparer les <em class="bl">établissements</em></h2>""",
     """    <h2><span class="n">2</span><span class="t">Comparer les <em class="bl">établissements</em></span></h2>"""),
    ("""      <h2><span class="n">3</span> Préparer les <em class="co">prochaines étapes</em></h2>""",
     """      <h2><span class="n">3</span><span class="t">Préparer les <em class="co">prochaines étapes</em></span></h2>"""),
])

patch('site.css', [
    ("""/* Pas de flex ici : il ferait de chaque nœud un item et supprimerait les espaces
   entre le texte nu et les <em> — « Parcourirsans calculer ». */
h2{font-size:clamp(1.5rem,3.4vw,2.25rem);line-height:1.2}""",
     """/* Un titre sans pastille reste un bloc de texte ordinaire : ni flex ni grille, qui
   feraient de chaque nœud un item séparé et supprimeraient les espaces entre le
   texte nu et les <em> — « Parcourirsans calculer ». */
h2{font-size:clamp(1.5rem,3.4vw,2.25rem);line-height:1.2}
/* Un titre numéroté prend deux colonnes : la pastille, puis TOUT le texte dans une
   seule cellule — ses espaces internes sont donc préservés, et ses lignes suivantes
   s'alignent sur la première au lieu de repartir sous la pastille. */
h2:has(.n){display:grid;grid-template-columns:auto minmax(0,1fr);gap:.7rem;align-items:center}
h2 .t{min-width:0}"""),

    ("""/* La pastille s'aligne seule sur la ligne de texte : elle est le seul élément qui
   demandait un alignement, pas le titre entier. */
h2 .n{width:2.4rem;height:2.4rem;margin-right:.7rem;border-radius:999px;background:var(--bl);color:#fff;
  display:inline-flex;align-items:center;justify-content:center;font-size:1.05rem;vertical-align:-.55rem}""",
     """/* Pas de décalage en rem : la taille du titre varie avec la largeur (clamp), donc
   une valeur fixe ne peut être juste qu'à une seule largeur. C'est la grille qui
   aligne, et la pastille garde sa taille propre. */
h2 .n{width:2.4rem;height:2.4rem;flex:0 0 auto;border-radius:999px;background:var(--bl);color:#fff;
  display:inline-flex;align-items:center;justify-content:center;font-size:1.05rem}
/* Repli pour un navigateur sans :has() — le titre reste lisible, la pastille sur sa ligne. */
@supports not selector(:has(*)){ h2 .n{margin-right:.7rem;vertical-align:-.5rem} }"""),
])

print('%d blocs posés' % n)
