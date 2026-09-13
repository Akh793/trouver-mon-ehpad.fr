# -*- coding: utf-8 -*-
"""Page de retours : mise en page, et le bouton de thème enfin à droite partout.

Trois corrections :

1. `.head-act` était un conteneur flex sans alignement déclaré, donc collé à
   gauche. Sur l'accueil, son parent `.head-side` le tirait à droite et masquait
   le défaut ; sur les pages annexes, qui n'ont pas ce parent, le bouton de thème
   se retrouvait en haut à gauche, au-dessus du fil d'Ariane.

2. Le contenu des pages annexes était calé à gauche d'une fenêtre large : un
   bloc de 52 rem et beaucoup de vide à droite. Il se centre.

3. L'encadré d'avertissement empilait trois paragraphes sur une colonne étroite,
   ce qui en faisait un mur vertical. Ses trois mises en garde deviennent trois
   colonnes dès que la place le permet : même contenu, trois fois moins haut.
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


# ── 1. Le bouton de thème, à droite sur toutes les pages
patch('site.css', [
    (".head-act{display:flex;align-items:center;gap:.6rem}",
     """/* Aligné à droite explicitement : sur l'accueil, le parent .head-side le tirait
   déjà de ce côté, ce qui masquait l'absence de règle ici. Les pages annexes,
   elles, n'ont pas ce parent — le bouton de thème y partait à gauche. */
.head-act{display:flex;align-items:center;justify-content:flex-end;gap:.6rem}"""),
])

# ── 2 et 3. La mise en page propre à /retours/
patch('build_retours.py', [
    ("""STYLE = \"\"\"
.lead{font-size:1.05rem;color:var(--mut);max-width:60ch}
.avert{margin:1.4rem 0;padding:1rem 1.2rem;border-radius:var(--r2);background:var(--ti-or);
  border:1px solid var(--bd2);font-size:.9rem;line-height:1.5;max-width:66ch}
.avert p{margin:0 0 .6rem} .avert p:last-child{margin-bottom:0}""",

     """STYLE = \"\"\"
/* Ces règles ne valent que pour cette page : elles sont écrites dans son corps,
   pas dans la feuille partagée. */
#layout header, .page{margin-inline:auto}
.page{max-width:62rem}
#layout header{max-width:62rem;text-align:center}
#layout header .fil{display:block}
.lead{font-size:1.05rem;color:var(--mut);max-width:62ch;margin-inline:auto;text-align:center}
/* Trois mises en garde côte à côte plutôt qu'empilées : même texte, trois fois
   moins de hauteur, et chacune se lit d'un coup d'œil. */
.avert{margin:1.6rem auto;padding:1.1rem 1.3rem;border-radius:var(--r2);background:var(--ti-or);
  border:1px solid var(--bd2);font-size:.88rem;line-height:1.5;
  display:grid;gap:1rem 1.6rem;grid-template-columns:repeat(auto-fit,minmax(16rem,1fr))}
.avert p{margin:0}
.page h2{text-align:center}"""),

    (""".r-liste{margin-top:.8rem;display:grid;gap:.8rem;max-width:46rem}""",
     """.r-liste{margin-top:.8rem;display:grid;gap:.8rem;max-width:46rem;margin-inline:auto}"""),

    ("""#form-retour{max-width:40rem;margin-top:.8rem}""",
     """#form-retour{max-width:40rem;margin:.8rem auto 0}"""),

    ("""#form-retour .fld{margin-bottom:1rem}""",
     """#form-retour .fld{margin-bottom:1rem}
#form-retour button{display:block;margin-inline:auto}"""),

    (""".r-etat{margin-top:.8rem;padding:.6rem .9rem;border-radius:var(--r2);font-size:.9rem;max-width:40rem}""",
     """.r-etat{margin:.8rem auto 0;padding:.6rem .9rem;border-radius:var(--r2);font-size:.9rem;max-width:40rem;text-align:center}"""),

    ("""<p class="f-src">Les messages sont écrits par des visiteurs""",
     """<p class="f-src" style="max-width:46rem;margin-inline:auto">Les messages sont écrits par des visiteurs"""),
])

print('%d blocs posés' % n)
