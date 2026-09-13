# -*- coding: utf-8 -*-
"""Grille de saisie et cartes de résultat : délimitation et retour au survol.

Grille de saisie — les quatre champs n'avaient ni fond, ni bordure, ni padding :
rien ne disait où finissait « Où chercher » et où commençait « Dans un rayon de ».
Chacun devient une cellule à part entière, qui se soulève au survol.

Trois précautions, et la raison de chacune :
  1. l'effet est SUSPENDU dès que la cellule contient le focus (`:focus-within`) —
     sinon on saisit un montant dans un champ qui flotte sous le curseur ;
  2. la cellule au focus reçoit un `z-index` explicite — un `transform` crée un
     contexte d'empilement, et la liste déroulante des communes passerait sinon
     SOUS les cellules voisines malgré son z-index de 1200 ;
  3. pas de rotation 3D : elle désaligne la grille et floute le texte des champs.
     Un décalage vertical, une ombre qui s'ouvre et un agrandissement de 1 %
     donnent le même volume perçu, sans ces défauts.

Cartes de résultat — le CSS interdisait jusqu'ici toute animation dessus, par
prudence : elles sont nombreuses et se redessinent à chaque filtre. La liste
étant paginée par quinze, et `transform` comme `box-shadow` étant traitées par
le compositeur sans recalcul de mise en page, le coût est nul. L'état de survol
croisé depuis la carte (`.survol`) reste sans mouvement : rien ne doit bouger
sous un pointeur qui n'est pas là.
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


# ── 1. La grille : quatre cellules délimitées
rem(
    """.grid4{margin-top:1.4rem;display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(230px,1fr))}""",
    """.grid4{margin-top:1.4rem;display:grid;gap:.9rem;grid-template-columns:repeat(auto-fit,minmax(230px,1fr))}
/* Chaque critère de recherche occupe sa propre surface : sans elle, les quatre
   champs flottaient dans le même bandeau blanc et rien ne les séparait. */
.grid4 .fld{background:var(--surf);border:1px solid var(--bd2);border-radius:var(--r2);
  padding:.9rem .9rem 1rem;transition:transform .16s ease-out,box-shadow .16s ease-out,border-color .16s ease-out}
.grid4 .fld label{color:var(--ink);font-size:.88rem}
.grid4 .fld .fld-h{margin-top:.45rem}
/* Le relief au survol : décalage, ombre et 1 % d'agrandissement. Jamais de
   rotation — elle désalignerait la grille et flouterait le texte des champs. */
@media (hover:hover){
  .grid4 .fld:hover{transform:translateY(-3px) scale(1.01);
    box-shadow:0 10px 24px rgba(37,72,255,.13);border-color:var(--bl-t)}
  .grid4 .fld:hover label{color:var(--bl-t)}
}
/* Dès qu'on saisit, plus aucun mouvement : le champ ne doit pas flotter sous le
   curseur. Le z-index garde la liste des communes au-dessus des cellules voisines,
   qu'un transform ferait passer devant elle. */
.grid4 .fld:focus-within{transform:none;z-index:20;
  border-color:var(--bl-t);box-shadow:0 6px 18px rgba(37,72,255,.10)}
.grid4 .fld:focus-within label{color:var(--bl-t)}
@media (prefers-reduced-motion:reduce){
  .grid4 .fld{transition:none}
  .grid4 .fld:hover{transform:none}
}"""
)

# ── 2. Les cartes de résultat : un relief discret, en gris
rem(
    """.res:hover,.res.survol{border-color:var(--bd);background:var(--bg)}""",
    """/* L'ancienne consigne excluait toute animation ici. `transform` et `box-shadow`
   étant composées sans recalcul de mise en page, et la liste étant paginée par
   quinze, le coût est nul. Le relief reste gris : le bleu est réservé à la
   sélection, qui a son propre état juste en dessous. */
.res:hover,.res.survol{border-color:var(--bd);background:var(--bg)}
@media (hover:hover){
  .res:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(var(--om),.10);border-color:var(--mut2)}
  .res:hover .res-n{color:var(--ink)}
}
/* `.survol` vient du pointeur posé sur la carte, pas sur cette ligne : on change
   la couleur, jamais la position — rien ne doit bouger là où personne ne pointe. */
@media (prefers-reduced-motion:reduce){ .res:hover{transform:none} }"""
)

# la transition doit inclure transform, sinon le relief apparaît d'un coup
rem(
    """transition:border-color .15s,box-shadow .15s,background .15s;break-inside:avoid}""",
    """transition:transform .16s ease-out,border-color .15s,box-shadow .15s,background .15s;break-inside:avoid}"""
)

# la carte sélectionnée garde son relief bleu, le survol ne l'écrase pas
rem(
    """.res[aria-current="true"]{border-color:var(--bl-t);border-left-color:var(--bl-t);background:var(--ti-bl2);box-shadow:0 4px 14px rgba(37,72,255,.12)}""",
    """.res[aria-current="true"]{border-color:var(--bl-t);border-left-color:var(--bl-t);background:var(--ti-bl2);box-shadow:0 4px 14px rgba(37,72,255,.12)}
@media (hover:hover){
  .res[aria-current="true"]:hover{border-color:var(--bl-t);box-shadow:0 10px 24px rgba(37,72,255,.18)}
}"""
)

io.open(P, 'w', encoding='utf-8').write(s)
print('%d blocs posés' % n)
