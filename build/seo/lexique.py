# -*- coding: utf-8 -*-
"""Lexique du site et page dédiée au GIR (29/09/2026).

Les définitions viennent de build/lexique.json : 50 termes, chacun vérifié le 29/09/2026 sur une
source officielle consultée ce jour-là (service-public.fr, pour-les-personnes-agees.gouv.fr, CNSA,
HAS, BOFiP…), avec son statut ✅ / ⚠️. Aucune définition n'est écrite ici à la main.

Une seule page /lexique/, une ancre par terme : cinquante petites pages ressembleraient à du contenu
produit en masse. Seul le GIR, sans page d'approfondissement jusqu'ici et très recherché, a la sienne,
nourrie de données (répartition des résidents, tarifs dépendance médians).
"""
import json, os, statistics
import layout
from base import esc, nb, eur, eur2, mois_eur, MARQUE, MAJ, MAJ_ISO, DOMAINE, AUTEUR, AUTEUR_URL

B = os.path.dirname(os.path.abspath(__file__))
DONNEES = json.load(open(os.path.join(B, '..', 'lexique.json'), encoding='utf-8'))
TERMES = DONNEES['termes']
VERIF = '/'.join(reversed(DONNEES['verifie_le'].split('-')))   # « 29/09/2026 »
GIR = DONNEES['gir_page']

FAMILLES = [
    ('etablissements', 'Les établissements'),
    ('autonomie', 'L’autonomie'),
    ('tarifs', 'Les tarifs et la facture'),
    ('aides', 'Les aides et la famille'),
    ('demarches', 'Les démarches'),
    ('donnees', 'Les données et la qualité'),
]
URL = '/lexique/'
URL_GIR = '/guides/gir-niveau-autonomie/'

# Répartition des résidents d'EHPAD par GIR au 31/12/2023 : DREES, Badiane 2023, tableau 11,
# ligne « Ensemble » (France entière). Fichier téléchargé et lu le 10/09/2026 (build/audit/badiane2023.xlsx).
BADIANE_GIR = {'12': 327012, '34': 231317, '56': 32505, 'total': 590834}


def _cle_tri(t):
    import unicodedata
    s = unicodedata.normalize('NFD', t['terme']).encode('ascii', 'ignore').decode().lower()
    return s


def _source(t):
    return f'<a href="{esc(t["source_url"])}" rel="noopener">{esc(t["source_label"].split(" (")[0])}</a>'


def page_lexique(ecrire):
    tri = sorted(TERMES, key=_cle_tri)
    lettres = sorted({_cle_tri(t)[0].upper() for t in tri})
    index = ' '.join(f'<a href="#lettre-{l}">{l}</a>' for l in lettres)
    blocs = []
    for fam, titre in FAMILLES:
        lot = sorted((t for t in TERMES if t['famille'] == fam), key=_cle_tri)
        items = []
        for t in lot:
            plus = (f' · <a href="{t["lien"]}">En savoir plus</a>' if t.get('lien') else '')
            prudence = ('<p class="lx-prud">Définition établie à partir d’une source partielle : à confirmer.</p>'
                        if t['statut'] != '✅' else '')
            items.append(f'''<div class="lx-terme" id="{t["id"]}">
<h3>{esc(t["terme"])}</h3>
<p>{esc(t["definition"])}</p>
<p class="lx-pv"><b>Pour vous&nbsp;:</b> {esc(t["pour_vous"])}</p>{prudence}
<p class="lx-src">Source&nbsp;: {_source(t)}{plus}</p>
</div>''')
        blocs.append(f'<section class="lx-fam"><h2 id="famille-{fam}">{titre}</h2>{"".join(items)}</section>')
    # index alphabétique : chaque lettre renvoie au premier terme qui commence par elle
    alpha = []
    for l in lettres:
        lot = [t for t in tri if _cle_tri(t)[0].upper() == l]
        alpha.append(f'<li id="lettre-{l}"><b>{l}</b> ' + ' · '.join(
            f'<a href="#{t["id"]}">{esc(t["terme"])}</a>' for t in lot) + '</li>')
    familles = ' · '.join(f'<a href="#famille-{f}">{esc(t)}</a>' for f, t in FAMILLES)
    corps = f"""<h1 class="p-h1">Lexique de l’EHPAD</h1>
<p class="p-sub">{len(TERMES)} mots de l’EHPAD expliqués simplement&nbsp;: GIR, APA, aide sociale, tarif dépendance,
évaluation HAS… Chaque définition cite sa source officielle.</p>
<p class="p-maj">Par <a href="{AUTEUR_URL}">{AUTEUR}</a> · définitions vérifiées le {VERIF}</p>
<p>Sur tout le site, ces mots sont soulignés en pointillé&nbsp;: survolez-les pour la définition courte,
cliquez pour arriver ici.</p>
<nav class="lx-nav" aria-label="Familles de termes"><p>{familles}</p></nav>
<section><h2>De A à Z</h2><ul class="lx-alpha">{''.join(alpha)}</ul></section>
{''.join(blocs)}
<p class="src-bloc">Chaque définition a été vérifiée le {VERIF} sur la source citée. Une définition vous paraît
fausse ou incomplète&nbsp;? <a href="mailto:contact@trouver-mon-ehpad.fr?subject=Lexique">Signalez-le</a>.</p>"""
    ld = [{"@type": "DefinedTermSet", "@id": DOMAINE + URL + '#lexique', "name": "Lexique de l’EHPAD",
           "inLanguage": "fr-FR", "url": DOMAINE + URL,
           "hasDefinedTerm": [{"@type": "DefinedTerm", "@id": DOMAINE + URL + '#' + t['id'], "name": t['terme'],
                               "description": t['definition'], "url": DOMAINE + URL + '#' + t['id'],
                               "inDefinedTermSet": DOMAINE + URL + '#lexique'} for t in tri]}]
    ecrire(URL, layout.page(URL, 'Lexique EHPAD : GIR, APA, ASH et 50 mots expliqués',
        'GIR, APA, aide sociale à l’hébergement, tarif dépendance, habilitation, évaluation HAS : 50 mots de l’EHPAD '
        'expliqués simplement, avec leur source officielle.',
        corps, [('Accueil', '/'), ('Lexique', None)], ld_extra=ld, type_page='guide'), 0.7, 'contenus')


def guide_gir(ctx):
    """Entrée pour contenus.GUIDES : (slug, titre, sous-titre, corps, faq)."""
    rows = ctx['rows']
    cla = [r for r in rows if r.get('reg') != 'exp']
    med = {}
    for g, k in (('1-2', 't12'), ('3-4', 't34'), ('5-6', 't56')):
        v = [r[k] for r in cla if r.get(k)]
        med[g] = (statistics.median(v), len(v)) if v else (None, 0)
    n12, n34, n56, tot = BADIANE_GIR['12'], BADIANE_GIR['34'], BADIANE_GIR['56'], BADIANE_GIR['total']
    p = lambda x: nb(100 * x / tot, 0) + '&nbsp;%'
    niveaux = ''.join(f'<li><b>GIR {n["gir"]}</b>&nbsp;: {esc(n["description"])}</li>' for n in GIR['niveaux'])
    lignes = ''.join(
        f'<tr><td>GIR {g}</td><td class="num" data-l="Médiane par jour">{eur2(med[g][0])}</td>'
        f'<td class="num" data-l="Par mois">{eur(mois_eur(med[g][0]))}</td></tr>' if med[g][0] else ''
        for g in ('1-2', '3-4', '5-6'))
    n_tarifs = max(v[1] for v in med.values())
    def src(lst):
        vus, out = set(), []
        for x in lst:
            if x['url'] in vus: continue
            vus.add(x['url'])
            out.append(f'<a href="{esc(x["url"])}" rel="noopener">{esc(x["label"].split(" (")[0])}</a>')
        return ' · '.join(out)
    qe = GIR['qui_evalue']
    corps = f"""<div class="note"><b>En résumé.</b> Le GIR mesure la perte d’autonomie, de GIR&nbsp;1 (la plus forte)
à GIR&nbsp;6 (autonome). En EHPAD, il est évalué par le médecin coordonnateur. Il décide du tarif dépendance facturé
et du droit à l’allocation personnalisée d’autonomie (APA), ouverte du GIR&nbsp;1 au GIR&nbsp;4.</div>
<p class="src-l">Informations de cette page vérifiées le {VERIF} sur les sources citées.</p>
<section><h2>Les six niveaux</h2><ul>{niveaux}</ul>
<p class="src-l">Source&nbsp;: {src(GIR['niveaux_sources'])}</p></section>
<section><h2>Comment il est mesuré</h2><p>{esc(GIR['grille_aggir']['texte'])}</p>
<p class="src-l">Source&nbsp;: {src(GIR['grille_aggir']['sources'])}</p></section>
<section><h2>Qui l’évalue</h2>
<p><b>En EHPAD.</b> {esc(qe['en_ehpad']['texte'])}</p>
<p><b>À domicile.</b> {esc(qe['a_domicile']['texte'])}</p>
<p class="src-l">Sources&nbsp;: {src(qe['en_ehpad']['sources'] + qe['a_domicile']['sources'][:1])}</p></section>
<section><h2>Ce que le GIR change à la facture</h2>
<p>{esc(GIR['gir_et_tarif_dependance']['texte'])}</p>
<p>{esc(GIR['gir_et_apa']['texte'])}</p>
<div class="tbl-wrap"><table class="tbl"><caption>Tarif dépendance médian par GIR, hors territoires de l’expérimentation
de fusion (CNSA, {nb(n_tarifs)} établissements ayant déclaré ce tarif)</caption>
<thead><tr><th>Niveau</th><th class="num">Médiane par jour</th><th class="num">Soit par mois</th></tr></thead>
<tbody>{lignes}</tbody></table></div>
<p>Le tarif GIR&nbsp;5-6 reste à la charge de tous les résidents&nbsp;: c’est le ticket modérateur. Au-delà,
l’APA prend en charge tout ou partie de l’écart, selon les ressources.</p>
<div class="att">{esc(GIR['gir_et_tarif_dependance']['exception'])}
<a href="/etudes/fusion-soins-dependance-ehpad/">Les établissements concernés</a></div>
<p class="src-l">Sources&nbsp;: {src(GIR['gir_et_tarif_dependance']['sources'][:2] + GIR['gir_et_apa']['sources'][:1])}</p></section>
<section><h2>Qui vit en EHPAD, par GIR</h2>
<p>Au 31 décembre 2023, les EHPAD accueillaient {nb(tot)} résidents&nbsp;: <b>{p(n12)} en GIR&nbsp;1-2</b>,
{p(n34)} en GIR&nbsp;3-4 et {p(n56)} en GIR&nbsp;5-6. La plupart des personnes qui entrent en EHPAD ont
donc une perte d’autonomie forte.</p>
<p class="src-l">Source&nbsp;: DREES, <a href="https://www.data.gouv.fr/datasets/datadrees-badiane" rel="noopener">Badiane 2023</a>, tableau 11, France entière.</p></section>
<section><h2>Faire réévaluer ou contester</h2>
<p>{esc(GIR['reviser_ou_contester']['reevaluation']['texte'])}</p>
<p>{esc(GIR['reviser_ou_contester']['contestation']['texte'])}</p>
<p class="src-l">Sources&nbsp;: {src(GIR['reviser_ou_contester']['reevaluation']['sources'][:1] + GIR['reviser_ou_contester']['contestation']['sources'])}</p></section>
<section><h2>Le GIR dans le calculateur</h2><p>Si vous ne connaissez pas le GIR, le calculateur pose quatre
questions simples pour l’estimer, et le signale dans le résultat. Seul le GIR notifié fait foi.</p>
<p><a class="cta-b" href="/#bande-situation">Estimer le reste à charge</a></p></section>"""
    faq = [('Le GIR 5 ou 6 donne-t-il droit à l’APA&nbsp;?',
            'Non. L’APA est ouverte du GIR 1 au GIR 4. En GIR 5 ou 6, une aide peut être demandée à la caisse de retraite.'),
           ('Qui fixe le GIR en EHPAD&nbsp;?',
            'Le médecin coordonnateur de l’établissement, avec l’équipe soignante, en général un mois après l’entrée.')]
    return ('gir-niveau-autonomie', 'Le GIR, de 1 à 6 : le niveau d’autonomie expliqué',
            'Ce que mesure chaque GIR, qui l’évalue, et ce qu’il change à la facture.', corps, faq)
