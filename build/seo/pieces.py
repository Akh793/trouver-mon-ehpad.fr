# -*- coding: utf-8 -*-
"""Briques de contenu réutilisées par toutes les pages : chiffres clés, tableaux, appels à l'action,
questions fréquentes, blocs de sources. Aucune de ces briques n'invente de donnée : ce qui n'est pas
connu n'est pas affiché."""
import json
from base import esc, eur, nb, pct, mois_eur, MOIS, CNSA_MAJ, MAJ, AUTEUR, AUTEUR_URL

NON_PUB = '<span class="non">non publiée</span>'
STATUTS = {0: 'Public', 1: 'Associatif', 2: 'Privé commercial'}
STATUT_LONG = {0: 'public', 1: 'privé à but non lucratif (associatif)', 2: 'privé commercial'}


def kpis(items):
    """items : (valeur, libellé, mise_en_avant)"""
    h = ['<div class="kpis">']
    for v, lib, *r in items:
        cls = ' bl' if (r and r[0]) else ''
        h.append(f'<div class="kpi{cls}"><b>{v}</b><span>{esc(lib)}</span></div>')
    h.append('</div>')
    return ''.join(h)


def cta(href, libelle, ev, note=None, second=None):
    h = [f'<div class="cta"><a class="cta-b" href="{href}" data-ev="{ev}">{esc(libelle)}</a>']
    if second:
        h.append(f'<a class="cta-s" href="{second[0]}" data-ev="{second[2]}">{esc(second[1])}</a>')
    if note:
        h.append(f'<span class="cta-n">{note}</span>')
    h.append('</div>')
    return ''.join(h)


def ash_cell(v):
    if v == 1: return '<span class="oui">Oui</span>'
    if v == 2: return '<span class="oui">À confirmer</span>'
    if v == 0: return '<span class="non">Non</span>'
    return '<span class="non">Inconnu</span>'


def tableau(lot, url_de, legende, avec_ville=False, limite=None, evol=False):
    """Tableau comparatif d'établissements. Trié du moins cher au plus cher,
    les tarifs non déclarés en fin de liste."""
    lot = sorted(lot, key=lambda r: (r['p'] is None, r['p'] or 0))
    if limite: lot = lot[:limite]
    h = ['<div class="tbl-wrap"><table class="tbl">',
         f'<caption>{legende}</caption><thead><tr><th>Établissement</th>']
    if avec_ville: h.append('<th>Commune</th>')
    h.append('<th class="num">Hébergement</th>' + ('<th class="num">Depuis 2018</th>' if evol else '')
             + '<th>Aide sociale</th><th class="num">Places</th><th>Évaluation</th></tr></thead><tbody>')
    for r in lot:
        pm = eur(mois_eur(r['p'])) + '/mois' if r['p'] else '<span class="non">non déclaré</span>'
        h.append(f'<tr><td><a href="{url_de(r)}">{esc(r["nom_aff"])}</a></td>')
        if avec_ville: h.append(f'<td data-l="Commune">{esc(r["ville_nom"])}</td>')
        note = r['hasN'] or NON_PUB
        ev = ''
        if evol:
            se = r.get('serie')
            ev = (f'<td class="num" data-l="Évolution">{pct(se["e"], 0)} <small>({se["d"]}→{se["f"][2:]})</small></td>'
                  if se and se.get('e') is not None else '<td class="num" data-l="Évolution">—</td>')
        h.append(f'<td class="num" data-l="Hébergement">{pm}</td>{ev}'
                 f'<td data-l="Aide sociale">{ash_cell(r["ash"])}</td>'
                 f'<td class="num" data-l="Places">{r["cap"] or "—"}</td>'
                 f'<td data-l="Évaluation">{note}</td></tr>')
    h.append('</tbody></table></div>')
    return ''.join(h)


def qa(paires):
    """Questions fréquentes : rendu visible + balisage identique au texte affiché."""
    if not paires: return '', None
    h = ['<section><h2>Questions fréquentes</h2><div class="qa">']
    for q, a in paires:
        h.append(f'<details><summary><span>{esc_ent(q)}</span></summary><p>{a}</p></details>')
    h.append('</div></section>')
    ld = {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": _txt(q),
         "acceptedAnswer": {"@type": "Answer", "text": _txt(a)}} for q, a in paires]}
    return ''.join(h), ld


def esc_ent(s):
    """Échappe un texte qui contient déjà des entités HTML (« &nbsp; » notamment).

    esc() transforme « & » en « &amp; » : appliqué tel quel à « France&nbsp;? », il produit
    « &amp;nbsp; », que le navigateur affiche littéralement. On résout donc les entités en
    vrais caractères AVANT d'échapper — l'espace insécable reste un espace insécable."""
    import html as _h
    return esc(_h.unescape(s))


def _txt(html_str):
    """Texte nu, pour les données structurées : ni balise, ni entité, ni espace insécable.
    Google lit ces chaînes telles quelles — « &nbsp; » y serait affiché en toutes lettres."""
    import re, html as _h
    t = re.sub(r'<[^>]+>', ' ', html_str)          # les balises deviennent des espaces
    t = _h.unescape(t).replace('\u00a0', ' ')      # entités résolues, insécables normalisés
    return re.sub(r'\s+', ' ', t).strip()


SOURCES_PRIX = (f'<b>Sources</b>&nbsp;: tarifs CNSA ({CNSA_MAJ}) · identité et habilitation FINESS · évaluations HAS. '
                f'Mois = tarif journalier × {str(MOIS).replace(".", ",")}. Règles vérifiées le {MAJ}. '
                f'Responsable de la publication&nbsp;: <a href="{AUTEUR_URL}">{AUTEUR}</a>. '
                f'<a href="/notre-methodologie.html">Méthode</a> · '
                f'<a href="mailto:contact@trouver-mon-ehpad.fr?subject=Correction">Signaler une erreur</a>')


GUIDES_LIENS = [
    ('/guides/comment-choisir-un-ehpad/', 'Choisir un EHPAD'),
    ('/guides/questions-a-poser-lors-dune-visite/', 'Les questions à poser en visite'),
    ('/guides/dossier-admission-ehpad/', 'Le dossier d’admission'),
    ('/guides/tarif-hebergement-et-tarif-dependance/', 'Hébergement et dépendance'),
    ('/guides/comparer-deux-ehpad/', 'Comparer deux EHPAD'),
    ('/guides/pourquoi-les-prix-varient/', 'Pourquoi les prix varient'),
    ('/guides/trouver-une-place-en-ehpad/', 'Trouver une place'),
    ('/guides/ehpad-public-prive-ou-associatif/', 'Public, privé ou associatif'),
    ('/guides/ehpad-alzheimer-unite-protegee/', 'Alzheimer et unité protégée'),
    ('/guides/urgence-apres-hospitalisation/', 'Après une hospitalisation'),
    ('/guides/qui-paie-quand-la-retraite-ne-suffit-pas/', 'Quand la retraite ne suffit pas'),
    ('/aides-ehpad/obligation-alimentaire/', 'L’obligation alimentaire'),
]


def guides_tournants(cle, n=3, d_abord=None):
    """Quelques guides par page, choisis de façon stable (même page → mêmes liens) mais répartis sur
    l'ensemble du site, pour qu'aucun guide ne dépende d'un seul lien entrant."""
    import zlib
    k = zlib.crc32(str(cle).encode()) % len(GUIDES_LIENS)
    choix = [g for g in (d_abord or [])]
    i = k
    while len(choix) < n:
        g = GUIDES_LIENS[i % len(GUIDES_LIENS)]
        if g not in choix: choix.append(g)
        i += 5
    return ('<p class="guides-l"><b>Guides</b>&nbsp;: '
            + ' · '.join(f'<a href="{u}">{t}</a>' for u, t in choix) + '</p>')


def sources(txt=None):
    return f'<p class="src-bloc">{txt or SOURCES_PRIX}</p>'


def explique_heberg(reg=None):
    base = ('<p class="def">Le <b>tarif d’hébergement</b> est la part de la facture qui couvre la chambre, '
            'les repas, le ménage et l’animation. Il est payé par le résident et sa famille. ')
    if reg == 'exp':
        return (base + 'S’y ajoute ici une <b>participation forfaitaire</b> à l’aide au quotidien&nbsp;: un montant '
                'journalier identique pour tous, sans tarif par GIR et sans allocation personnalisée d’autonomie, '
                'cette commune relevant de l’expérimentation de fusion des financements soins et dépendance. '
                'Le reste à charge réel est donc rarement égal au prix affiché.</p>')
    return (base + 'S’y ajoute un <b>tarif dépendance</b>, qui dépend du niveau de perte d’autonomie et qui est '
            'en grande partie pris en charge par l’allocation personnalisée d’autonomie (APA), versée par le '
            'département. Le reste à charge réel est donc rarement égal au prix affiché.</p>')


def bloc_financement(lien):
    return f"""<section><h2>Comment financer un EHPAD&nbsp;?</h2>
<p>Quatre aides peuvent réduire la facture, et elles se cumulent&nbsp;:</p>
<ul>
<li><b>L’allocation personnalisée d’autonomie (APA)</b> prend en charge une partie du tarif dépendance. Elle est versée par le département, sans condition de ressources, mais son montant en dépend. <a href="/aides-ehpad/apa/">Comment elle se calcule</a></li>
<li><b>L’aide au logement</b> (APL ou allocation de logement sociale) est versée par la caisse d’allocations familiales ou la Mutualité sociale agricole, si l’établissement est conventionné. <a href="/aides-ehpad/aide-au-logement/">Dans quels cas</a></li>
<li><b>La réduction d’impôt</b> couvre 25&nbsp;% des frais d’hébergement et de dépendance restants, dans la limite de 2&nbsp;500&nbsp;€ par an et par personne hébergée. <a href="/aides-ehpad/reduction-impot/">Qui peut en bénéficier</a></li>
<li><b>L’aide sociale à l’hébergement</b> intervient en dernier, quand les ressources et l’épargne ne suffisent pas. Elle n’est possible que dans un établissement habilité, elle peut être demandée aux enfants et elle est récupérée sur la succession. <a href="/aides-ehpad/aide-sociale-hebergement/">Ce qu’il faut savoir avant de la demander</a></li>
</ul>
{cta(lien, 'Estimer mon reste à charge', 'seo_financement_to_calculator', 'Le calcul se fait dans votre navigateur : aucune information n’est transmise.')}</section>"""
