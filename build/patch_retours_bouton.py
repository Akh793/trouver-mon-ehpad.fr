# -*- coding: utf-8 -*-
"""« Vos retours » en bouton, dans la barre du haut et dans la navigation d'accueil.

La barre porte déjà un bouton plein, « Calculer mon reste à charge », en corail :
c'est l'action principale du site. Un second bouton plein de la même famille lui
ferait concurrence. Celui-ci prend donc l'ambre déjà présent dans la palette —
assez franc pour attirer l'œil, assez distinct pour qu'on ne confonde pas les deux.

Sous 860 px, la barre du haut ne peut plus porter les deux sans tronquer ses
libellés : le bouton s'y efface et « Vos retours » reste accessible par le menu
« Naviguer », où il est ajouté pour toutes les tailles d'écran.
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


BOUTON = '<a href="/retours/" class="tb-avis">Vos retours</a>\n'

# ── Accueil : barre du haut, menu déroulant, navigation principale
patch('index.template.html', [
    ("""        <a href="#bande-situation" class="tb-cta">Calculer mon reste à charge</a>""",
     """        <a href="/retours/" class="tb-avis">Vos retours</a>
        <a href="#bande-situation" class="tb-cta">Calculer mon reste à charge</a>"""),
    ("""            <a href="notre-methodologie.html">Notre méthodologie</a>
          </nav>""",
     """            <a href="notre-methodologie.html">Notre méthodologie</a>
            <a href="/retours/">Vos retours</a>
          </nav>"""),
    ("""      <a href="#bande-faq">Questions fréquentes</a>
    </nav>""",
     """      <a href="#bande-faq">Questions fréquentes</a>
      <a href="/retours/" class="nav-avis">Vos retours</a>
    </nav>"""),
])

# ── Pages annexes : même barre, même menu
patch('build_pages.py', [
    ("""<a href="/" class="tb-cta">Calculer mon reste à charge</a>""",
     BOUTON + """<a href="/" class="tb-cta">Calculer mon reste à charge</a>"""),
    ("""<a href="/qui-sommes-nous.html">Qui sommes-nous&nbsp;?</a>
</nav>""",
     """<a href="/qui-sommes-nous.html">Qui sommes-nous&nbsp;?</a>
<a href="/retours/">Vos retours</a>
</nav>"""),
])

patch('site.css', [
    (""".tb-cta{background:var(--co);color:#fff;border:0;border-radius:999px;font:inherit;font-size:.85rem;""",
     """/* Ambre, et non corail : le corail est réservé à l'action principale du site.
   Deux boutons pleins de même teinte se disputeraient le regard. */
.tb-avis{background:var(--orange);color:#fff;border:0;border-radius:999px;font:inherit;font-size:.85rem;
  font-weight:600;padding:.6rem 1.1rem;min-height:38px;display:inline-flex;align-items:center;
  text-decoration:none;white-space:nowrap;box-shadow:0 4px 14px rgba(224,138,0,.3);
  transition:transform .15s,box-shadow .15s}
.tb-avis:hover{transform:translateY(-1px);box-shadow:0 6px 18px rgba(224,138,0,.42)}
/* Dans la navigation d'accueil, même couleur mais en pastille discrète : cette
   rangée est une liste de liens, pas une barre d'actions. */
.nav-avis{background:var(--ti-or);color:var(--sur-or);border-radius:999px;
  padding:.15rem .7rem;font-weight:600}
.nav-avis:hover{background:var(--orange);color:#fff}
@media (hover:none){.tb-avis:hover{transform:none}}
@media (prefers-reduced-motion:reduce){.tb-avis{transition:none}.tb-avis:hover{transform:none}}
/* Sous 860 px, la barre ne peut plus porter les deux boutons sans tronquer ses
   libellés : celui-ci s'efface, et « Vos retours » reste dans le menu Naviguer. */
@media (max-width:860px){.tb-avis{display:none}}
.tb-cta{background:var(--co);color:#fff;border:0;border-radius:999px;font:inherit;font-size:.85rem;"""),
])

print('%d blocs posés' % n)
