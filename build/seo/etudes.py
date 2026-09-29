# -*- coding: utf-8 -*-
"""Actifs citables (P3, 29/09/2026) : données ouvertes, baromètre annuel détaillé, étude sur la fusion
soins-dépendance, page presse. Tout est recalculé à chaque construction à partir des mêmes données que
les fiches : aucun chiffre n'est saisi à la main."""
import csv, io, os, json, statistics, collections
import geo, layout
from base import (esc, nb, eur, eur2, pct, mois_eur, stats, mediane, MOIS, MARQUE, MAJ, MAJ_ISO,
                  CNSA_MAJ, DOMAINE, AUTEUR, AUTEUR_URL, SITE, ANNEES)
from pieces import kpis, cta, sources
from territoires import phrase_dep, med_mois

import datetime as _dt
AUJ_FR = _dt.date.today().strftime('%d/%m/%Y')
INFL = {'2019': 1.1, '2020': 0.5, '2021': 1.6, '2022': 5.2, '2023': 4.9, '2024': 2.0, '2025': 0.9}
LICENCE = 'https://www.etalab.gouv.fr/licence-ouverte-open-licence'
F_CSV = '/donnees/evolution-prix-ehpad-2018-2025.csv'
F_DICO = '/donnees/evolution-prix-ehpad-2018-2025-dictionnaire.csv'
CITATION = f'Données : {MARQUE} (trouver-mon-ehpad.fr), à partir des tarifs déclarés à la CNSA, fichiers annuels 2018-2025'


# ------------------------------------------------------------------ calculs
def serie_annuelle(rows):
    """Par année : tarif médian (€/jour), variation médiane établissement par établissement (années
    consécutives uniquement), part des établissements en baisse. Même méthode que le baromètre."""
    out = []
    for i, a in enumerate(ANNEES):
        vals = [r['serie']['p'][i] for r in rows if r.get('serie') and r['serie']['p'][i]]
        var = []
        if i:
            for r in rows:
                s = r.get('serie')
                if s and s['p'][i] and s['p'][i - 1]:
                    var.append(100 * (s['p'][i] - s['p'][i - 1]) / s['p'][i - 1])
        out.append({'annee': a, 'med': mediane(vals), 'n': len(vals),
                    'var': statistics.median(var) if var else None, 'nvar': len(var),
                    'baisse': (100 * sum(1 for v in var if v < 0) / len(var)) if var else None})
    return out


def territoire_exp(r):
    return 'Métropole de Lyon' if r['dep'] == '69' else geo.DEPARTEMENTS[r['dep']]


# ------------------------------------------------------------ données ouvertes
DICO = [
    ('finess', 'texte', 'Numéro FINESS de l’établissement (géographique)', 'FINESS, Agence du numérique en santé'),
    ('nom', 'texte', 'Nom de l’établissement, remis en forme (casse, acronymes)', 'FINESS'),
    ('commune', 'texte', 'Commune d’implantation', 'FINESS / COG INSEE'),
    ('code_insee', 'texte', 'Code officiel géographique de la commune', 'FINESS'),
    ('departement', 'texte', 'Code du département', 'calcul'),
    ('statut', 'texte', 'public, associatif, prive_commercial ou vide si non publié', 'CNSA, fichier retraité 2020'),
    ('habilitation_aide_sociale', 'texte', 'oui, non, a_confirmer (tarif « aide sociale » déclaré sans habilitation au répertoire) ou vide', 'FINESS + CNSA'),
    ('regime_dependance', 'texte', 'classique, ou experimentation_fusion (territoires de l’article 79 LFSS 2024)', 'calcul à partir du territoire'),
] + [(f'prix_{a}', 'nombre', f'Prix d’hébergement permanent, chambre seule, en euros par jour, déclaré en {a}', f'CNSA, fichier annuel {a}') for a in ANNEES] + [
    ('evolution_pct', 'nombre', 'Évolution en % entre la première et la dernière année connues', 'calcul'),
    ('annee_debut', 'nombre', 'Première année connue', 'calcul'),
    ('annee_fin', 'nombre', 'Dernière année connue', 'calcul'),
    ('url_fiche', 'texte', 'Adresse de la fiche de l’établissement sur trouver-mon-ehpad.fr', 'trouver-mon-ehpad.fr'),
]
STATUT_CSV = {0: 'public', 1: 'associatif', 2: 'prive_commercial'}
ASH_CSV = {1: 'oui', 0: 'non', 2: 'a_confirmer'}


def exporter(ctx):
    rows = [r for r in ctx['rows'] if r.get('serie')]
    rows.sort(key=lambda r: r['fin'])
    os.makedirs(os.path.join(SITE, 'donnees'), exist_ok=True)
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=';', lineterminator='\n')
    w.writerow([c for c, *_ in DICO])
    for r in rows:
        s = r['serie']
        w.writerow([r['fin'], r['nom_aff'], r['ville_nom'], r['insee'], r['dep'],
                    STATUT_CSV.get(r['statut'], ''), ASH_CSV.get(r['ash'], ''),
                    'experimentation_fusion' if r.get('reg') == 'exp' else 'classique']
                   + [('%.2f' % v).replace('.', ',') if v else '' for v in s['p']]
                   + [str(s['e']).replace('.', ','), s['d'], s['f'],
                      DOMAINE + ctx['url_fiche'][r['fin']] if r['fin'] in ctx['url_fiche'] else ''])
    open(os.path.join(SITE, F_CSV.lstrip('/')), 'w', encoding='utf-8-sig').write(buf.getvalue())
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=';', lineterminator='\n')
    w.writerow(['colonne', 'type', 'description', 'source'])
    for x in DICO: w.writerow(x)
    open(os.path.join(SITE, F_DICO.lstrip('/')), 'w', encoding='utf-8-sig').write(buf.getvalue())
    return len(rows)


# ---------------------------------------------------------------------- pages
def page_donnees(ctx, ecrire, n):
    taille = os.path.getsize(os.path.join(SITE, F_CSV.lstrip('/'))) // 1024
    corps = f"""<h1 class="p-h1">Données ouvertes</h1>
<p class="p-sub">Le prix de chaque EHPAD année par année, de 2018 à 2025 — une série qu’aucune source publique ne publie
établissement par établissement.</p>
<p class="p-maj">Fichier produit le {AUJ_FR} · Licence Ouverte 2.0</p>
<section><h2>Évolution du prix d’hébergement des EHPAD, 2018-2025</h2>
<p><b>{nb(n)} établissements</b>, une ligne chacun&nbsp;: identité, commune, statut, habilitation à l’aide sociale, régime
de financement de la dépendance, prix d’hébergement d’une chambre seule pour chaque année de 2018 à 2025, évolution.
Fichier CSV, séparateur point-virgule, encodage UTF-8, {taille} Ko.</p>
{cta(F_CSV, 'Télécharger le fichier (CSV)', 'donnees_csv', None, (F_DICO, 'Dictionnaire des colonnes', 'donnees_dico'))}
<ul>
<li><b>Source</b>&nbsp;: fichiers annuels « prix hébergement et tarifs dépendance des EHPAD » publiés par la Caisse
nationale de solidarité pour l’autonomie sur data.gouv.fr (2018 à 2025), joints sur le numéro FINESS&nbsp;; identité
et habilitation&nbsp;: répertoire FINESS.</li>
<li><b>Méthode</b>&nbsp;: le prix retenu est celui de l’hébergement permanent en chambre seule, tel que déclaré par
l’établissement. Une année manque quand l’établissement n’a pas déclaré. Aucun prix n’est estimé.
<a href="/notre-methodologie.html">Méthodologie complète</a>.</li>
<li><b>Licence</b>&nbsp;: <a href="{LICENCE}">Licence Ouverte 2.0</a>. Mention à reprendre&nbsp;: « {esc(CITATION)} ».</li>
</ul></section>
<section><h2>Ce qu’on peut en faire</h2>
<p>Mesurer la hausse des prix dans un territoire, comparer établissements publics et privés, repérer les
établissements dont le prix a le plus augmenté depuis une date donnée. Les agrégats sont déjà calculés dans le
<a href="/etudes/barometre-prix-ehpad-2026/">baromètre</a> et le <a href="/prix-ehpad-par-departement/">classement
des départements</a>.</p></section>
{sources()}"""
    ld = [{"@type": "Dataset", "name": "Évolution du prix d’hébergement des EHPAD, établissement par établissement, 2018-2025",
           "description": f"Prix d’hébergement permanent en chambre seule déclaré chaque année à la CNSA par {n} EHPAD, de 2018 à 2025, avec statut, habilitation à l’aide sociale et régime de financement de la dépendance.",
           "url": DOMAINE + '/donnees/', "inLanguage": "fr-FR", "isAccessibleForFree": True,
           "creator": {"@id": DOMAINE + "/#organization"}, "license": LICENCE,
           "temporalCoverage": "2018/2025", "spatialCoverage": {"@type": "Country", "name": "France"},
           "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": DOMAINE + F_CSV}]}]
    ecrire('/donnees/', layout.page('/donnees/', 'Données ouvertes : prix des EHPAD 2018-2025',
        f'Le prix d’hébergement de {nb(n)} EHPAD, année par année de 2018 à 2025, en téléchargement libre (CSV, Licence Ouverte).',
        corps, [('Accueil', '/'), ('Données ouvertes', None)], ld_extra=ld, type_page='etude'), 0.7, 'contenus')


def page_fusion(ctx, ecrire):
    rows = ctx['rows']
    exp = [r for r in rows if r.get('reg') == 'exp']
    cla = [r for r in rows if r.get('reg') != 'exp']
    pf = (exp[0].get('pf') or {}).get('montant_jour') if exp else None
    par_t = collections.defaultdict(list)
    for r in exp: par_t[territoire_exp(r)].append(r)
    lig = []
    for t, lot in sorted(par_t.items(), key=lambda x: -len(x[1])):
        s = stats(lot)
        u = ctx['url_dep'].get(lot[0]['dep'])
        nom = f'<a href="{u}">{esc(t)}</a>' if u and t != 'Métropole de Lyon' else esc(t)
        lig.append(f'<tr><td>{nom}</td><td class="num" data-l="EHPAD">{len(lot)}</td>'
                   f'<td class="num" data-l="Tarif médian">{med_mois(s)}</td>'
                   f'<td class="num" data-l="Habilités">{s["ash"]}</td></tr>')
    ident = [r for r in exp if r['t12'] and r['t56'] and abs(r['t12'] - r['t56']) < 0.01]
    avec_gir = [r for r in exp if r['t12'] and r['t56']]
    # ce que paie un résident aux ressources modestes, hors aide au logement : hébergement + part dépendance
    m_exp = mediane([r['p'] + pf for r in exp if r['p'] and pf])
    m_cla = mediane([r['p'] + r['t56'] for r in cla if r['p'] and r['t56']])
    s_exp, s_cla = stats(exp), stats(cla)
    corps = f"""<h1 class="p-h1">Fusion soins-dépendance&nbsp;: {nb(len(exp))} EHPAD ont changé de règles</h1>
<p class="p-sub">Depuis le 1<sup>er</sup> juillet 2025, dans 23 territoires, l’allocation personnalisée d’autonomie en
établissement a disparu. Combien d’établissements sont concernés, où, et ce que cela change pour la facture.</p>
<p class="p-maj">Par <a href="{AUTEUR_URL}">{AUTEUR}</a> · calculé le {AUJ_FR} sur les {nb(len(rows))} EHPAD ouverts</p>
{kpis([(nb(len(exp)), 'EHPAD dans le régime expérimental', True),
       (nb(100 * len(exp) / len(rows), 0) + ' %', 'des EHPAD de France'),
       (eur2(pf) + ' / jour' if pf else '—', 'participation identique pour tous en 2026'),
       (str(len(par_t)), 'territoires')])}
<section><h2>Le chiffre que personne ne publie</h2>
<p>La CNSA liste les 23 territoires expérimentateurs, mais ne publie pas le nombre d’établissements concernés.
En rapprochant la commune de chaque EHPAD de cette liste, nous en comptons <b>{nb(len(exp))}</b>, soit
<b>{nb(100 * len(exp) / len(rows), 1)} %</b> des {nb(len(rows))} EHPAD ouverts. Méthode&nbsp;: le régime vient du
territoire d’implantation (pour la Métropole de Lyon, de la liste de ses communes), jamais des tarifs déclarés.</p>
<p>Signe que les déclarations suivent la réforme&nbsp;: {nb(len(ident))} de ces {nb(len(exp))} établissements déclarent
désormais un tarif unique pour les trois niveaux de GIR{f", et aucun de ceux qui déclarent des tarifs dépendance n’en déclare de différents" if len(ident) == len(avec_gir) else f" ({nb(len(avec_gir) - len(ident))} déclarent encore des tarifs différents)"}&nbsp;; les {nb(len(exp) - len(avec_gir))} autres n’ont pas
déclaré de tarif dépendance.</p></section>

<section><h2>Territoire par territoire</h2>
<div class="tbl-wrap"><table class="tbl"><caption>EHPAD relevant de l’expérimentation, tarif d’hébergement médian mensuel</caption>
<thead><tr><th>Territoire</th><th class="num">EHPAD</th><th class="num">Tarif médian</th><th class="num">Habilités à l’aide sociale</th></tr></thead>
<tbody>{''.join(lig)}</tbody></table></div></section>

<section><h2>Ce qui change pour la facture</h2>
<ul>
<li>Avant&nbsp;: un tarif dépendance par GIR, l’allocation personnalisée d’autonomie qui en couvre l’essentiel, et une
participation du résident qui augmente avec ses ressources au-delà de 2 846,77 € par mois.</li>
<li>Maintenant&nbsp;: une <b>participation forfaitaire de {eur2(pf) if pf else '—'} par jour</b>, la même pour tous, quels que
soient le GIR et les ressources.</li>
<li>Pour un résident aux ressources modestes, la différence est faible&nbsp;: le forfait remplace le tarif GIR 5-6
qu’il payait déjà. Pour un résident aux ressources élevées et très dépendant, l’économie peut être nette.</li>
</ul>
<p>Hébergement plus part dépendance à la charge d’un résident aux ressources inférieures à 2 846,77 €, médiane mensuelle&nbsp;:
<b>{eur(mois_eur(m_exp)) if m_exp else '—'}</b> dans le régime expérimental, <b>{eur(mois_eur(m_cla)) if m_cla else '—'}</b>
ailleurs. {phrase_ecart(s_exp, s_cla)}</p>
<p><a href="/aides-ehpad/apa/#fusion">Les règles de l’expérimentation</a> · sources&nbsp;:
<a href="https://www.pour-les-personnes-agees.gouv.fr/actualites/financement-des-ehpad-une-experimentation-dans-23-departements">portail
national des personnes âgées</a>, <a href="https://www.cnsa.fr/budget-et-financement/modeles-tarifaires/reforme-de-la-tarification-des-ehpad">CNSA</a>.</p></section>

<section><h2>Reprendre ces chiffres</h2>
<p>Libres de reprise avec la mention «&nbsp;{esc(CITATION)}&nbsp;». La liste des établissements, avec leur régime, est
dans le <a href="/donnees/">fichier de données ouvertes</a>. <a href="/presse/">Espace presse</a>.</p></section>
{sources()}"""
    ld = [{"@type": "Article", "headline": f"Fusion soins-dépendance : {len(exp)} EHPAD ont changé de règles",
           "author": {"@id": DOMAINE + "/#editeur"}, "publisher": {"@id": DOMAINE + "/#organization"},
           "datePublished": "2026-09-29", "dateModified": "2026-09-29", "inLanguage": "fr-FR",
           "mainEntityOfPage": DOMAINE + '/etudes/fusion-soins-dependance-ehpad/'}]
    ecrire('/etudes/fusion-soins-dependance-ehpad/', layout.page('/etudes/fusion-soins-dependance-ehpad/',
        f'Fusion soins-dépendance : {len(exp)} EHPAD concernés',
        f'{nb(len(exp))} EHPAD, soit {nb(100 * len(exp) / len(rows), 0)} % du parc, relèvent de l’expérimentation de fusion soins-dépendance : territoires, tarifs, effet sur la facture.',
        corps, [('Accueil', '/'), ('Études', '/etudes/'), ('Fusion soins-dépendance', None)],
        ld_extra=ld, type_page='etude'), 0.8, 'contenus')
    return len(exp)


def phrase_ecart(s_exp, s_cla):
    """L'écart de facture vient-il de l'hébergement ? On le dit seulement si les chiffres le montrent."""
    a, b = s_exp['med'], s_cla['med']
    if not (a and b): return ''
    if abs(a - b) / b < 0.02:
        return f'Le tarif d’hébergement médian est comparable (médiane {med_mois(s_exp)} contre {med_mois(s_cla)}).'
    sens = 'plus élevé' if a > b else 'plus bas'
    return (f'L’écart tient d’abord au tarif d’hébergement, {sens} dans ces territoires (médiane {med_mois(s_exp)} '
            f'contre {med_mois(s_cla)}), sur lequel la réforme ne porte pas.')


def bloc_annuel(rows):
    """Tableau année par année, pour le baromètre."""
    sa = serie_annuelle(rows)
    lig = []
    for x in sa:
        inf = INFL.get(x['annee'])
        lig.append(f'<tr><td>{x["annee"]}</td><td class="num" data-l="Tarif médian / jour">{eur2(x["med"])}</td>'
                   f'<td class="num" data-l="Hausse médiane">{pct(x["var"], 2) if x["var"] is not None else "—"}</td>'
                   f'<td class="num" data-l="Inflation">{pct(inf) if inf is not None else "—"}</td>'
                   f'<td class="num" data-l="En baisse">{nb(x["baisse"], 1) + " %" if x["baisse"] is not None else "—"}</td></tr>')
    d24 = next(x for x in sa if x['annee'] == '2024'); d25 = next(x for x in sa if x['annee'] == '2025')
    return sa, f"""<section><h2>Année par année</h2>
<p>La hausse est mesurée <b>établissement par établissement</b>, entre deux années consécutives, puis on en prend la
médiane&nbsp;: c’est ce qu’a vécu un résident type, indépendamment des ouvertures et fermetures. En 2024, les prix ont
augmenté de <b>{pct(d24['var'], 2)}</b> pour une inflation de 2,0 %&nbsp;; en 2025, de <b>{pct(d25['var'], 2)}</b> pour
0,9 %.</p>
<div class="tbl-wrap"><table class="tbl"><caption>Tarif d’hébergement, chambre seule — sources&nbsp;: CNSA (fichiers annuels), INSEE (inflation)</caption>
<thead><tr><th>Année</th><th class="num">Tarif médian / jour</th><th class="num">Hausse médiane</th><th class="num">Inflation</th><th class="num">Établissements en baisse</th></tr></thead>
<tbody>{''.join(lig)}</tbody></table></div>
<p><a href="/donnees/">Télécharger les données, établissement par établissement</a></p></section>"""


def page_presse(ctx, ecrire, n_exp, n_csv):
    rows = ctx['rows']; s = ctx['FR']
    sa = serie_annuelle(rows)
    d24 = next(x for x in sa if x['annee'] == '2024'); d25 = next(x for x in sa if x['annee'] == '2025')
    dd = sorted(((stats(l)['med'], d) for d, l in ctx['par_dep'].items() if stats(l)['med']))
    corps = f"""<h1 class="p-h1">Presse et partenaires</h1>
<p class="p-sub">Les chiffres clés, prêts à citer, les données brutes et la personne à contacter.</p>
<p class="p-maj">Chiffres recalculés le {AUJ_FR} à partir des tarifs déclarés à la CNSA ({CNSA_MAJ})</p>
<section><h2>Les chiffres clés</h2>
<ul>
<li><b>{med_mois(s)} par mois</b>&nbsp;: tarif d’hébergement médian d’une chambre seule, sur {nb(s['n_prix'])} EHPAD ayant déclaré leur prix.</li>
<li><b>{pct(s['evol_med'])}</b>&nbsp;: hausse médiane du tarif depuis 2018, mesurée établissement par établissement, contre +17,2 % d’inflation.</li>
<li><b>{pct(d24['var'], 2)} en 2024 et {pct(d25['var'], 2)} en 2025</b>, pour une inflation de 2,0 % et 0,9 %.</li>
<li><b>{nb(n_exp)} EHPAD</b> ({nb(100 * n_exp / len(rows), 0)} % du parc) relèvent de l’expérimentation de fusion soins-dépendance&nbsp;: un chiffre que la CNSA ne publie pas. <a href="/etudes/fusion-soins-dependance-ehpad/">L’étude</a></li>
<li>De <b>{med_mois(stats(ctx['par_dep'][dd[0][1]]))}</b> ({esc(geo.DEPARTEMENTS[dd[0][1]])}) à <b>{med_mois(stats(ctx['par_dep'][dd[-1][1]]))}</b> ({esc(geo.DEPARTEMENTS[dd[-1][1]])})&nbsp;: tarif médian par département. <a href="/prix-ehpad-par-departement/">Le classement</a></li>
<li><b>{nb(s['ash'])} EHPAD sur {nb(s['n'])}</b> sont habilités à l’aide sociale à l’hébergement.</li>
</ul>
<p>Mention à reprendre&nbsp;: « {esc(CITATION)} ».</p></section>
<section><h2>Les données</h2>
<p><a href="/donnees/">Le prix de {nb(n_csv)} EHPAD, année par année de 2018 à 2025</a> (CSV, Licence Ouverte)&nbsp;;
<a href="/etudes/barometre-prix-ehpad-2026/">le baromètre</a>&nbsp;; chaque établissement a sa fiche, avec son rang dans le
département et l’évolution de son prix.</p></section>
<section><h2>Qui sommes-nous</h2>
<p>Trouver mon EHPAD est un service gratuit, indépendant, sans publicité ni partenariat avec des établissements, édité
par <a href="{AUTEUR_URL}">{AUTEUR}</a>. Il n’est pas un service public. Les calculs sont reproductibles à partir des
sources publiques citées sur chaque page.</p></section>
<section><h2>Contact</h2>
<p><a href="mailto:contact@trouver-mon-ehpad.fr?subject=Presse">contact@trouver-mon-ehpad.fr</a> — réponse sous 48 heures.
Nous pouvons produire un extrait par département, par statut ou pour une liste d’établissements.</p></section>"""
    ecrire('/presse/', layout.page('/presse/', 'Presse : chiffres clés et données sur les EHPAD',
        f'Tarif médian {med_mois(s)} par mois, hausse de {pct(s["evol_med"])} depuis 2018, {nb(n_exp)} EHPAD en fusion soins-dépendance : chiffres prêts à citer et données.',
        corps, [('Accueil', '/'), ('Presse', None)], type_page='etude'), 0.6, 'contenus')


def construire(ctx, ecrire):
    n = exporter(ctx)
    page_donnees(ctx, ecrire, n)
    n_exp = page_fusion(ctx, ecrire)
    page_presse(ctx, ecrire, n_exp, n)
    print(f'données ouvertes : {n} établissements ; fusion : {n_exp} EHPAD')
