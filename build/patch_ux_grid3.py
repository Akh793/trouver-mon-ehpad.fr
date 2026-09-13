# -*- coding: utf-8 -*-
"""Le bloc « Préciser la situation » reçoit le même découpage que la grille principale,
et les listes déroulantes cessent de tronquer leur libellé.

Le texte d'un `select` passait SOUS la flèche : celle-ci est dessinée en fond, à
18 px du bord droit, sans qu'aucun padding ne lui réserve la place. « Aucun, ou je
ne veux pas le calculer » se coupait donc en plein milieu du dernier mot. Réduire
la police ne suffisait pas : il fallait aussi réserver la gouttière.
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


# ── 1. Les douze champs du bloc « Préciser la situation » deviennent des cellules
rem(
    ".grid3{margin-top:.8rem;display:grid;gap:1rem 1.6rem;grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}",
    ".grid3{margin-top:.8rem;display:grid;gap:.9rem;grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}"
)

# ── 2. Le style de cellule vaut pour les deux grilles
for avant, apres in [
    (".grid4 .fld{background", ".grid4 .fld,.grid3 .fld{background"),
    (".grid4 .fld label{color", ".grid4 .fld label,.grid3 .fld label{color"),
    (".grid4 .fld .fld-h{margin-top", ".grid4 .fld .fld-h,.grid3 .fld .fld-h{margin-top"),
    ("  .grid4 .fld:hover{transform", "  .grid4 .fld:hover,.grid3 .fld:hover{transform"),
    ("  .grid4 .fld:hover label{color", "  .grid4 .fld:hover label,.grid3 .fld:hover label{color"),
    (".grid4 .fld:focus-within{transform", ".grid4 .fld:focus-within,.grid3 .fld:focus-within{transform"),
    (".grid4 .fld:focus-within label{color", ".grid4 .fld:focus-within label,.grid3 .fld:focus-within label{color"),
    ("  .grid4 .fld{transition:none}", "  .grid4 .fld,.grid3 .fld{transition:none}"),
    ("  .grid4 .fld:hover{transform:none}", "  .grid4 .fld:hover,.grid3 .fld:hover{transform:none}"),
]:
    rem(avant, apres)

# ── 3. Les listes déroulantes : place réservée à la flèche, police ajustée
rem(
    "select{cursor:pointer;-webkit-appearance:none;appearance:none;",
    """select{cursor:pointer;-webkit-appearance:none;appearance:none;
  /* la flèche est dessinée en fond à 18 px du bord : sans cette gouttière, le
     libellé le plus long passe dessous et se coupe en plein mot */
  padding-right:2.4rem;font-size:.94rem;text-overflow:ellipsis;"""
)

io.open(P, 'w', encoding='utf-8').write(s)
print('%d blocs posés' % n)
