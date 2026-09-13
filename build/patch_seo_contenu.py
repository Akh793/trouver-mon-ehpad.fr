# -*- coding: utf-8 -*-
"""Les pages de contenu décrivaient l'ancien modèle de calcul.

La réduction d'impôt y figurait comme une ligne de soustraction du reste à charge,
au même rang que l'APA et l'aide au logement. Ce n'est pas la même chose : l'une
diminue la facture chaque mois, l'autre arrive l'année suivante, plafonnée, et
seulement si la personne paie de l'impôt. L'expérimentation de fusion des
financements, qui concerne vingt-trois territoires, n'était mentionnée nulle part.
"""
import io, os, sys

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'seo', 'contenus.py')
s = io.open(P, encoding='utf-8').read()
n = 0


def rem(a, b):
    global s, n
    if a not in s:
        print('INTROUVABLE :', a[:120].replace('\n', ' '))
        sys.exit(1)
    s = s.replace(a, b, 1)
    n += 1


rem(
    """<p>Le tarif affiché n’est pas le reste à charge. Après l’allocation personnalisée d’autonomie, l’aide au logement et
la réduction d’impôt, l’écart se compte souvent en centaines d’euros par mois — et il dépend entièrement de la
situation de la personne.</p>""",
    """<p>Le tarif affiché n’est pas ce qu’il faut sortir chaque mois. L’allocation personnalisée d’autonomie et l’aide
au logement viennent en déduction de la facture&nbsp;; la réduction d’impôt, elle, n’arrive que l’année suivante et
ne diminue pas la dépense mensuelle. L’écart se compte souvent en centaines d’euros par mois, et il dépend
entièrement de la situation de la personne.</p>"""
)

rem(
    """    corps = f\"\"\"<div class="note"><b>La réponse courte.</b> On additionne le tarif d’hébergement et le tarif
dépendance, puis on retire l’allocation personnalisée d’autonomie, l’aide au logement et la réduction d’impôt.
Ce qui reste est le reste à charge. Pour un tarif médian et une retraite modeste, il représente souvent une à
deux fois le montant de la retraite.</div>

<section><h2>Les cinq lignes du calcul</h2>
<ol>
<li><b>Hébergement</b> — le tarif journalier de l’établissement, multiplié par {str(MOIS).replace('.', ',')} jours (la durée moyenne d’un mois).</li>
<li><b>Dépendance</b> — le tarif correspondant au niveau d’autonomie de la personne, mesuré par la grille officielle GIR.</li>
<li><b>Moins l’allocation personnalisée d’autonomie</b> — versée directement à l’établissement par le département. Jusqu’à 2 846,77 € de ressources par mois, le résident ne paie que le tarif dépendance le plus faible. Au-delà de 4 379,64 €, sa participation est plafonnée. <a href="/aides-ehpad/apa/">Le détail</a></li>
<li><b>Moins l’aide au logement</b> — si l’établissement est conventionné. Son montant est notifié par la caisse d’allocations familiales ou la Mutualité sociale agricole. <a href="/aides-ehpad/aide-au-logement/">Dans quels cas</a></li>
<li><b>Moins la réduction d’impôt</b> — 25 % des frais d’hébergement et de dépendance restants, dans la limite de 2 500 € par an et par personne hébergée, et seulement si la personne paie de l’impôt sur le revenu. <a href="/aides-ehpad/reduction-impot/">Qui y a droit</a></li>
</ol></section>""",
    """    corps = f\"\"\"<div class="note"><b>La réponse courte.</b> Trois montants, à ne pas confondre. La <b>facture</b> de
l’établissement&nbsp;: hébergement plus aide au quotidien. Ce qu’il faut <b>sortir chaque mois</b>&nbsp;: la facture
moins les aides versées à l’établissement. Et, à part, un <b>avantage fiscal</b> qui arrive l’année suivante et ne
diminue aucune mensualité. Pour un tarif médian et une retraite modeste, la somme à sortir représente souvent une
à deux fois le montant de la retraite.</div>

<section><h2>1. Ce que l’établissement facture</h2>
<ol>
<li><b>Hébergement</b> — le tarif journalier de l’établissement, multiplié par {str(MOIS).replace('.', ',')} jours (la durée moyenne d’un mois).</li>
<li><b>Aide au quotidien</b> — dans la plupart des départements, le tarif dépendance correspondant au niveau
d’autonomie de la personne, mesuré par la grille officielle GIR. Dans vingt-trois territoires qui expérimentent
depuis le 1<sup>er</sup> juillet 2025 la fusion des financements soins et dépendance, c’est à la place une
<b>participation forfaitaire</b> de 6,16 € par jour en 2026, identique pour tous&nbsp;: ni le GIR ni les ressources
n’y changent quoi que ce soit.</li>
</ol></section>

<section><h2>2. Ce qu’il faut sortir chaque mois</h2>
<ol>
<li><b>Moins l’allocation personnalisée d’autonomie</b> — versée directement à l’établissement par le département.
Jusqu’à 2 846,77 € de ressources par mois, le résident ne paie que le tarif dépendance le plus faible. Au-delà de
4 379,64 €, sa participation est plafonnée. Dans les territoires d’expérimentation, cette allocation en établissement
est <b>supprimée</b>&nbsp;: la participation forfaitaire en tient lieu. <a href="/aides-ehpad/apa/">Le détail</a></li>
<li><b>Moins l’aide au logement</b> — si l’établissement est conventionné. Son montant est notifié par la caisse
d’allocations familiales ou la Mutualité sociale agricole, <b>pour un établissement précis</b>&nbsp;: il n’est pas
transposable d’un EHPAD à l’autre. <a href="/aides-ehpad/aide-au-logement/">Dans quels cas</a></li>
</ol></section>

<section><h2>3. Et, séparément, la réduction d’impôt</h2>
<p>25 % des frais d’hébergement et de dépendance restants, dans la limite de 10 000 € de dépenses par an et par
personne hébergée, soit 2 500 € de réduction au maximum. Elle ne se retranche <b>pas</b> de la somme à sortir chaque
mois&nbsp;: elle arrive l’année suivante, elle ne peut pas dépasser l’impôt réellement dû, et elle n’est pas
remboursée. Une personne non imposable n’en tire rien. <a href="/aides-ehpad/reduction-impot/">Qui y a droit</a></p></section>"""
)

rem(
    """<li>Tarif dépendance&nbsp;: environ 420 € par mois, dont l’essentiel est pris en charge par l’allocation personnalisée d’autonomie, puisque la retraite est inférieure à 2 846,77 €.</li>
<li>Aide au logement&nbsp;: dépend du conventionnement de l’établissement, à demander à la caisse d’allocations familiales.</li>
<li>Réduction d’impôt&nbsp;: nulle ici, la personne n’étant pas imposable.</li>
</ul>""",
    """<li>Aide au quotidien&nbsp;: environ 420 € par mois en régime de droit commun, dont l’essentiel est pris en charge
par l’allocation personnalisée d’autonomie, puisque la retraite est inférieure à 2 846,77 €. Dans un territoire
d’expérimentation, ce serait à la place une participation forfaitaire d’environ 188 € par mois, sans aucune aide
à déduire.</li>
<li>Aide au logement&nbsp;: dépend du conventionnement de l’établissement, à demander à la caisse d’allocations familiales.</li>
<li>Réduction d’impôt&nbsp;: nulle ici, la personne n’étant pas imposable — et de toute façon elle n’allègerait
aucune mensualité.</li>
</ul>"""
)

rem(
    """<div class="att">Cet exemple est une illustration, pas une simulation. Les tarifs dépendance varient d’un établissement
à l’autre, et le montant exact dépend de la situation complète de la personne.</div></section>""",
    """<div class="att">Cet exemple est une illustration, pas une simulation. Les tarifs varient d’un établissement à
l’autre, le régime de financement dépend du territoire, et le montant exact dépend de la situation complète de la
personne. Il ne comprend ni les frais du premier mois — dépôt de garantie, souvent trente jours d’hébergement,
frais de dossier, déménagement — ni les dépenses personnelles du quotidien.</div></section>"""
)

io.open(P, 'w', encoding='utf-8').write(s)
print('%d blocs corrigés' % n)
