# -*- coding: utf-8 -*-
"""Fiche d'un établissement : ce qu'il coûte, ce qu'il vaut, ce qui reste à payer."""
import collections, math
import geo, layout
from base import (esc, nb, eur, eur2, pct, mois_eur, stats, mediane, lien_calc, titre, MOIS,
                  MARQUE, MAJ, CNSA_MAJ, DOMAINE)
from pieces import kpis, cta, tableau, sources, explique_heberg, STATUTS, STATUT_LONG, ash_cell
from territoires import phrase_dep, med_mois, compare

INFL = 17.2
TARIF_SOINS = {
    'G': 'tarif global de soins : l’établissement rémunère lui-même les médecins et les auxiliaires médicaux, et paie les médicaments',
    'P': 'tarif partiel de soins : les médicaments et une partie des soins passent par les professionnels de ville, et sont remboursés comme à domicile',
    'V': 'petite unité de vie : établissement de petite taille, dont le financement des soins suit des règles particulières',
}


def bloc_ash(r):
    if r['ash'] == 1:
        return ('<p><b>Aide sociale à l’hébergement&nbsp;: oui.</b> Cet établissement peut accueillir des personnes '
                'dont les ressources ne suffisent pas à payer l’hébergement&nbsp;: le département complète, puis récupère '
                'tout ou partie des sommes versées sur la succession. L’information vient du libellé officiel du '
                'répertoire national des établissements (FINESS).</p>')
    if r['ash'] == 2:
        return ('<p><b>Aide sociale à l’hébergement&nbsp;: à confirmer.</b> Le répertoire officiel indique que cet '
                'établissement n’est pas habilité, alors qu’il déclare un tarif « aide sociale ». C’est le cas typique '
                'd’une habilitation limitée à quelques places. Posez directement la question à l’établissement.</p>')
    if r['ash'] == 0:
        return ('<p><b>Aide sociale à l’hébergement&nbsp;: non.</b> Si les ressources et l’épargne ne suffisent pas, '
                'cette aide ne pourra pas être demandée ici&nbsp;: il faudra chercher un établissement habilité.</p>')
    return ''


def bloc_qualite(r):
    out = []
    if r['hasN']:
        p = (f'<p><b>Évaluation officielle&nbsp;: note {r["hasN"]}</b> (échelle de A à D). '
             f'Évaluation réalisée le {esc(str(r["hasD"])[:10].split("-")[::-1] and "/".join(str(r["hasD"])[:10].split("-")[::-1]))}')
        if r['hasO']:
            p += f', par l’organisme {esc(r["hasO"])} — choisi et rémunéré par l’établissement lui-même'
        p += '.'
        if r['hasM'] is not None:
            p += f' Moyenne des objectifs évalués&nbsp;: {nb(r["hasM"], 2)} sur 100.'
        if r['hasCI'] is not None:
            p += f' Critères impératifs atteints&nbsp;: <b>{r["hasCI"]} sur 18</b>.'
        out.append(p + ' Source&nbsp;: Haute Autorité de santé.</p>')
    else:
        out.append('<p>Aucune évaluation n’a été publiée pour cet établissement par la Haute Autorité de santé. '
                   'Cela ne veut pas dire que l’établissement est mauvais&nbsp;: toutes les évaluations ne sont pas '
                   'encore réalisées ni publiées.</p>')
    if r['alim']:
        a = r['alim']
        d = '/'.join(str(a[1])[:10].split('-')[::-1]) if a[1] else ''
        out.append(f'<p><b>Hygiène alimentaire&nbsp;: {esc(a[0])}</b>, contrôle du {esc(d)}'
                   + (f' (suite donnée&nbsp;: {esc(a[2])})' if a[2] else '') +
                   '. Source&nbsp;: contrôles officiels de la Direction générale de l’alimentation.</p>')
    return ''.join(out)


def bloc_tarifs(r, ctx):
    l = []
    if r['p']:
        l.append(f'<li><b>Hébergement, chambre seule&nbsp;: {eur2(r["p"])} par jour</b>, soit environ '
                 f'<b>{eur(mois_eur(r["p"]))} par mois</b>' + (f', tarif déclaré en {esc(str(r["maj"]).split("-")[1])}/{esc(str(r["maj"]).split("-")[0])}' if r['maj'] else '') + '.</li>')
    if r['pcd']:
        l.append(f'<li>Hébergement, chambre double&nbsp;: {eur2(r["pcd"])} par jour, soit environ {eur(mois_eur(r["pcd"]))} par mois.</li>')
    if r['pa'] and r['ash'] in (1, 2):
        l.append(f'<li>Tarif « aide sociale »&nbsp;: {eur2(r["pa"])} par jour. C’est le tarif appliqué quand le département prend le relais.</li>')
    if r.get('reg') == 'exp':
        pf = r.get('pf') or {}
        m = pf.get('montant_jour') or 0
        l.append('<li><b>Aide au quotidien&nbsp;: participation forfaitaire</b> de '
                 f'{eur2(m)} par jour, soit environ {eur(mois_eur(m))} par mois. '
                 'Cette commune fait partie des territoires qui expérimentent, depuis le 1<sup>er</sup> juillet 2025, '
                 'la fusion des financements soins et dépendance&nbsp;: il n’y a plus de tarif par GIR, plus de '
                 'participation qui augmente avec les ressources, et l’allocation personnalisée d’autonomie en '
                 'établissement y est supprimée. Le montant est le même pour tous les résidents.</li>')
    elif r['t12'] and r['t56'] and abs(r['t12'] - r['t56']) > 0.01:
        l.append(f'<li>Tarif dépendance&nbsp;: de {eur2(r["t56"])} par jour pour une perte d’autonomie légère à '
                 f'{eur2(r["t12"])} pour une perte d’autonomie lourde. C’est la part largement couverte par '
                 f'l’allocation personnalisée d’autonomie, versée par le département.</li>')
    elif r['t12']:
        l.append(f'<li>Tarif dépendance&nbsp;: {eur2(r["t12"])} par jour. L’établissement déclare le même tarif '
                 f'pour tous les niveaux de perte d’autonomie&nbsp;: demandez-lui celui qui s’appliquera '
                 f'réellement, il varie normalement selon le niveau évalué par le département.</li>')
    else:
        l.append('<li>Tarif dépendance&nbsp;: non déclaré. C’est la part qui s’ajoute à l’hébergement et que '
                 'l’allocation personnalisée d’autonomie couvre en grande partie&nbsp;; demandez-la à l’établissement.</li>')
    if r['temp'] is not None:
        l.append(f'<li>Accueil temporaire&nbsp;: {eur2(r["temp"])} par jour — pour un séjour de quelques semaines, par exemple après une hospitalisation.</li>')
    if not l:
        return ('<p>Cet établissement n’a pas déclaré de tarif à la Caisse nationale de solidarité pour l’autonomie. '
                'Nous préférons l’écrire plutôt que d’afficher une estimation&nbsp;: demandez-lui son tarif du jour, '
                'il est obligatoire de le communiquer.</p>')
    return '<ul>' + ''.join(l) + '</ul>'


def bloc_evolution(r):
    s = r.get('serie')
    if not s or s.get('e') is None: return ''
    vals = [v for v in s['p'] if v]
    if len(vals) < 2: return ''
    ecart = s['e'] - INFL
    comp = (f'soit {pct(ecart)} par rapport à l’inflation, qui a été de 17,2 % sur la même période'
            if s['d'] == '2018' and s['f'] == '2025'
            else 'l’établissement n’ayant pas déclaré son tarif chaque année, l’évolution est mesurée entre ces deux dates seulement')
    return (f'<section><h2>L’évolution du tarif</h2><p>Le tarif d’hébergement de cet établissement est passé de '
            f'<b>{eur2(vals[0])} à {eur2(vals[-1])} par jour</b> entre {s["d"]} et {s["f"]}, soit <b>{pct(s["e"])}</b> '
            f'({pct(s["a"], 2)} par an) — {comp}. '
            f'Une hausse n’est pas nécessairement un mauvais signe&nbsp;: elle peut financer des travaux ou du personnel '
            f'supplémentaire. Elle vous dit surtout à quoi vous attendre pour les années à venir.</p></section>')


def bloc_pratique(r):
    l = []
    if r['cap']: l.append(f'<li>Capacité&nbsp;: {r["cap"]} places (donnée déclarée en 2020, dernière disponible en accès libre).</li>')
    if r['statut'] is not None: l.append(f'<li>Statut&nbsp;: établissement {STATUT_LONG[r["statut"]]}.</li>')
    if r['pm']: l.append(f'<li>Gestionnaire&nbsp;: {esc(r["pm"])}.</li>')
    if r['ouv']: l.append(f'<li>Ouvert depuis {esc(r["ouv"])}.</li>')
    if r['tarif'] in TARIF_SOINS:
        l.append(f'<li>Financement des soins&nbsp;: {TARIF_SOINS[r["tarif"]]}'
                 + (', avec une pharmacie interne' if r['pui'] else '') + '.</li>')
    if r['nIncl'] or r['nSus']:
        l.append(f'<li>{r["nIncl"] or 0} prestation(s) comprise(s) dans le tarif et {r["nSus"] or 0} facturée(s) en plus. '
                 f'Le fichier officiel ne dit pas lesquelles&nbsp;: demandez la liste à l’établissement.</li>')
    return '<ul>' + ''.join(l) + '</ul>' if l else ''


def fiche(ctx, ecrire, r, voisins):
    vn = ctx['nom_ville'].get(r['cle']) or r['ville_nom']
    d = r['dep']; dn = geo.DEPARTEMENTS[d]
    rs, rn = geo.region_de(d)
    sv = stats(ctx['par_ville'][r['cle']]) if r['cle'] in ctx['par_ville'] else None
    sd = stats(ctx['par_dep'][d])
    lien = lien_calc(cp=r['cp'], insee=r['insee'], rayon=20, finess=r['fin'])
    url = ctx['url_fiche'][r['fin']]
    nom = r['nom_aff']

    # comparaison — uniquement si elle est calculable
    comp = ''
    if r['p'] and sv and sv['med'] and sv['n_prix'] >= 3:
        e = 100 * (r['p'] - sv['med']) / sv['med']
        mot = 'moins cher' if e < 0 else 'plus cher'
        comp = (f'<p>Ce tarif est <b>{nb(abs(e), 0)} % {mot}</b> que le tarif médian des {sv["n_prix"]} EHPAD de '
                f'{esc(vn)} ayant déclaré leur tarif ({med_mois(sv)} par mois).</p>')
    elif r['p'] and sd['med']:
        e = 100 * (r['p'] - sd['med']) / sd['med']
        mot = 'moins cher' if e < 0 else 'plus cher'
        comp = (f'<p>Ce tarif est <b>{nb(abs(e), 0)} % {mot}</b> que le tarif médian {esc(phrase_dep(d))} '
                f'({med_mois(sd)} par mois).</p>')

    adr = ' '.join(x for x in [titre(r['adr']) if r['adr'] else None, r['cp'], vn] if x)
    tel = r['tel']
    tel_aff = ' '.join(tel[i:i + 2] for i in range(0, len(tel), 2)) if tel else None

    corps = f"""<h1 class="p-h1">{esc(nom)}</h1>
<p class="p-sub">EHPAD à {esc(vn)} ({esc(dn)}) — tarifs, aide sociale, évaluation et estimation du reste à charge.</p>
<div class="f-head">
<div class="f-grid">
<div><b>{eur(mois_eur(r['p'])) + '<small style="font-size:.75rem;font-weight:400">/mois</small>' if r['p'] else 'Non déclaré'}</b><span>hébergement, chambre seule</span></div>
<div><b>{r['cap'] or '—'}</b><span>places (2020)</span></div>
<div><b>{'Oui' if r['ash'] == 1 else ('À confirmer' if r['ash'] == 2 else ('Non' if r['ash'] == 0 else '—'))}</b><span>aide sociale à l’hébergement</span></div>
<div><b>{r['hasN'] or '—'}</b><span>évaluation officielle (A à D)</span></div>
</div>
<p class="f-adr">{esc(adr)}{f' · <a href="tel:{esc(tel)}">{esc(tel_aff)}</a>' if tel_aff else ''}</p>
</div>
{cta(lien, 'Estimer mon reste à charge', 'seo_establishment_to_calculator',
     'Le calculateur s’ouvre avec cet établissement déjà sélectionné : il sépare ce que l’établissement facture, ce qu’il faut sortir chaque mois après aides, et l’avantage fiscal de l’année suivante.')}

<section><h2>Les tarifs</h2>
{bloc_tarifs(r, ctx)}
{comp}
{explique_heberg(r.get('reg'))}</section>

{bloc_evolution(r)}

<section><h2>Payer moins&nbsp;: les aides possibles</h2>
{bloc_ash(r)}
<p>{"Ici, l’allocation personnalisée d’autonomie en établissement est supprimée : la participation forfaitaire en tient lieu. Reste " if r.get('reg') == 'exp' else "Avant l’aide sociale, deux aides réduisent la facture : " }<a href="/aides-ehpad/apa/">{"" if r.get('reg') == 'exp' else "l’allocation personnalisée d’autonomie, qui couvre une grande partie du tarif dépendance"}</a>{"" if r.get('reg') == 'exp' else " ; "}<a href="/aides-ehpad/aide-au-logement/">l’aide au logement</a>, si l’établissement est conventionné. <a href="/aides-ehpad/reduction-impot/">La réduction d’impôt</a> de 25 % des frais restants, elle, n’arrive que l’année suivante et seulement si la personne paie de l’impôt : elle n’allège aucune mensualité.</p></section>

<section><h2>La qualité&nbsp;: ce que disent les contrôles</h2>
{bloc_qualite(r)}
<p><a href="/guides/lire-une-evaluation-ehpad/">Comment lire une évaluation d’EHPAD</a></p></section>

<section><h2>L’établissement en pratique</h2>
{bloc_pratique(r)}</section>

<section><h2>Les EHPAD à proximité</h2>
<p>Les établissements les plus proches ayant déclaré un tarif. L’écart entre deux EHPAD distants de quelques kilomètres dépasse souvent 500&nbsp;€ par mois.</p>
{tableau(voisins, ctx['lien_de'], 'Établissements voisins, du tarif le plus bas au plus élevé', avec_ville=True) if voisins else '<p>Aucun autre établissement avec tarif déclaré dans les environs immédiats.</p>'}
<div class="liens-grid">
{f'<a class="lien-c" href="{ctx["url_ville"][r["cle"]]}"><b>Tous les EHPAD à {esc(vn)}</b><span>{sv["n"]} établissements, tarif médian {med_mois(sv)} par mois.</span></a>' if r['cle'] in ctx['url_ville'] and r['cle'] in ctx['villes_page'] else ''}
<a class="lien-c" href="{ctx['url_dep'][d]}"><b>Les EHPAD {esc(phrase_dep(d))}</b><span>{nb(sd['n'])} établissements, tarif médian {med_mois(sd)} par mois.</span></a>
<a class="lien-c" href="/calcul-reste-a-charge-ehpad/"><b>Calculer le reste à charge</b><span>La méthode, ligne par ligne.</span></a>
</div></section>
{sources()}"""

    ld = [{
        "@type": "Dataset",
        "name": f"Tarifs et caractéristiques publiques de l’EHPAD {nom} ({r['fin']})",
        "description": f"Tarif d’hébergement, tarifs dépendance, habilitation à l’aide sociale, capacité et évaluation officielle de l’EHPAD {nom} à {vn}.",
        "url": DOMAINE + url, "inLanguage": "fr-FR", "isAccessibleForFree": True,
        "creator": {"@id": DOMAINE + "/#organization"},
        "spatialCoverage": {"@type": "Place", "name": f"{vn}, {dn}, France"},
        "license": "https://www.etalab.gouv.fr/licence-ouverte-open-licence",
        "identifier": r['fin'], "dateModified": "2026-09-11",
    }]
    ariane = [('Accueil', '/'), ('Les EHPAD en France', '/ehpad/')]
    if rs: ariane.append((rn, ctx['url_region'][rs]))
    ariane.append((dn, ctx['url_dep'][d]))
    if r['cle'] in ctx['villes_page']: ariane.append((vn, ctx['url_ville'][r['cle']]))
    ariane.append((nom, None))

    titre_p = f'{nom} à {vn} : prix et reste à charge | {MARQUE}'
    desc = (f'Tarifs, habilitation à l’aide sociale, capacité et évaluation de l’EHPAD {nom} à {vn}'
            + (f'. Hébergement à partir de {eur(mois_eur(r["p"]))} par mois' if r['p'] else '')
            + '. Estimez votre reste à charge après les aides.')
    ecrire(url, layout.page(url, titre_p[:110], desc[:250], corps, ariane, ld_extra=ld,
                            type_page='etablissement', lieu=vn), 0.6, 'etablissements')


def construire(ctx, ecrire, liste):
    par_dep = collections.defaultdict(list)
    for r in liste: par_dep[r['dep']].append(r)
    for d, lot in par_dep.items():
        avec = [x for x in ctx['par_dep'][d] if x['p'] and x['lat'] and x['fin'] in ctx['url_fiche']]
        for r in lot:
            vois = []
            if r['lat']:
                for x in avec:
                    if x['fin'] == r['fin']: continue
                    dd = math.hypot((r['lat'] - x['lat']) * 111, (r['lon'] - x['lon']) * 111 * math.cos(math.radians(r['lat'])))
                    vois.append((dd, x))
                vois.sort(key=lambda t: t[0])
            fiche(ctx, ecrire, r, [x for _, x in vois[:6]])
