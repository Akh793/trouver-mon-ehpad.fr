# -*- coding: utf-8 -*-
"""Refonte rédactionnelle — lot 5 : le bas du parcours.

Le bloc « D'où viennent ces données ? » pesait 1 785 mots dans le parcours
principal : la liste complète des sources, un tableau d'inflation, deux
inventaires de lacunes et un paragraphe de périmètre de 150 mots. C'est de la
méthodologie, et elle a déjà sa page. Le parcours n'en garde que la promesse et
le lien ; rien n'est supprimé du site, tout reste accessible.

Un chiffre y était par ailleurs faux depuis la v2.5 : « Version 2.4 » et des
compteurs saisis à la main, que le bloc COUVERTURE recalcule désormais à chaque
build. Le paragraphe entier disparaît plutôt que d'entretenir deux vérités.
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
    ("""    <h2>D’où viennent <em class="bl">ces données</em> ?</h2>
    <p class="s-int">Chaque chiffre de cette page vient d’une base publique ou d’un texte officiel, et porte sa date. Dernière vérification des règles nationales : <strong class="meta-date"></strong>. Nous n’inventons aucun montant : quand une donnée n’est pas publiée, l’outil le dit au lieu de la remplacer par une valeur vraisemblable.</p>
    <div id="sources" class="src-grid"></div>

    <h3 class="h3b">La référence de comparaison des prix</h3>
    <p class="s-int">L’évolution du prix de chaque établissement est comparée à l’inflation constatée par l’INSEE (indice des prix à la consommation, ensemble des ménages, moyenne annuelle) :</p>
    <div class="infl-wrap">
      <table class="infl">
        <caption>Inflation annuelle en France, INSEE — cumul 2018 → 2025 : +17,2 %</caption>
        <thead><tr><th scope="col">Année</th><th scope="col">Inflation</th></tr></thead>
        <tbody id="infl-table"></tbody>
      </table>
    </div>

    <h3 class="h3b">Ce que ce site ne sait pas</h3>
    <p class="src-n">Chiffres recalculés à chaque mise à jour des données, jamais saisis à la main.</p>
    <ul id="couverture" class="non-sim"></ul>

    <h3 class="h3b">Ce que ce site ne calcule pas, et pourquoi</h3>
    <ul id="non-simule" class="non-sim"></ul>
    <p class="s-foot">Les seuils de l’APA en établissement utilisés ici : <b id="seuil-inf">—</b> et <b id="seuil-sup">—</b> de ressources mensuelles. Périmètre : 7 417 EHPAD ouverts au 11/09/2026, dont 5 793 déclarent un prix à la CNSA. Les 1 624 autres restent affichés avec la mention « prix non déclaré » — les faire disparaître reviendrait à récompenser l’opacité — et 67 établissements sans coordonnées connues n’apparaissent pas sur la carte. Habilitation à l’aide sociale, d’après le libellé officiel FINESS : 6 081 habilités, 1 142 non habilités, 194 à confirmer (l’établissement déclare un tarif aide sociale à la CNSA sans être habilité dans FINESS). Historique de prix disponible pour 7 255 établissements, taux d’occupation du segment pour 6 602. Chaque établissement documenté, chaque ville et chaque département ont aussi leur page&nbsp;: <a href="/ehpad/">voir l’annuaire</a>. Version 2.4.</p>""",

     """    <h2>D’où viennent <em class="bl">ces données</em> ?</h2>
    <p class="s-int">Les tarifs et informations proviennent de sources publiques. Leur date figure dans chaque fiche.</p>
    <p class="s-int"><a class="lien" href="notre-methodologie.html">Sources et méthode</a> · <a class="lien" href="/ehpad/">L’annuaire des établissements</a></p>

    <details class="bloc-plus">
      <summary><b>Ce que ce site ne sait pas</b> <span>— mesuré à chaque mise à jour des données</span></summary>
      <ul id="couverture" class="non-sim"></ul>
      <ul id="non-simule" class="non-sim"></ul>
    </details>
    <div hidden><div id="sources"></div><table><tbody id="infl-table"></tbody></table>
      <b id="seuil-inf"></b><b id="seuil-sup"></b></div>"""),

    # ── Le titre des démarches
    ("""  <!-- ============ BANDE 5 : QUESTIONS FRÉQUENTES ============ -->""",
     """  <!-- ============ BANDE 5 : QUESTIONS FRÉQUENTES ============ -->"""),
])

print('%d blocs posés' % n)
