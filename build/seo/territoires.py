# -*- coding: utf-8 -*-
"""Pages France → région → département → ville."""
import os, json, collections
import geo, layout
from base import (esc, nb, eur, pct, mois_eur, stats, mediane, lien_calc, slug, B,
                  DOMAINE, MARQUE, MAJ, CNSA_MAJ, MOIS)
from layout import titre_page, titre_court, desc_courte
from pieces import kpis, cta, tableau, qa, sources, explique_heberg, bloc_financement, STATUTS, guides_tournants

A = os.path.join(B, 'audit')
ASH = json.load(open(os.path.join(B, 'ash_dept.json'), encoding='utf-8'))
BAD = json.load(open(os.path.join(A, 'badiane_dept.json'), encoding='utf-8'))
ASH_CODE = {'2A': '20R', '2B': '20R', '69': '69D'}
INFL = 17.2


def phrase_dep(code):
    return geo.OU_DEP[code]


def phrase_region(rs, rn):
    return geo.OU_REGION.get(rs, 'en ' + rn)


def med_mois(s):
    return eur(mois_eur(s['med'])) if s['med'] else 'non déclaré'


def phrase_prix(s, ou, ref=None, mot_ref=None):
    """Paragraphe du tarif médian. Si aucun tarif n'est déclaré, on l'écrit — on n'estime pas."""
    if not s['med']:
        return (f'<p>Aucun des {s["n"]} établissements {ou} n’a déclaré son tarif à la Caisse nationale de '
                f'solidarité pour l’autonomie. Nous préférons l’écrire plutôt que d’afficher une estimation&nbsp;: '
                f'demandez le tarif du jour à l’établissement, il est tenu de le communiquer.</p>')
    p = (f'<p>Le tarif d’hébergement médian {ou} est de <b>{med_mois(s)} par mois</b> pour une chambre seule, '
         f'sur {s["n_prix"]} établissement{"s" if s["n_prix"] > 1 else ""} ayant déclaré leur tarif.')
    if ref and mot_ref: p += compare(s['med'], ref, mot_ref)
    if s['q1'] and s['q3']:
        p += f' La moitié des établissements se situe entre {eur(mois_eur(s["q1"]))} et {eur(mois_eur(s["q3"]))} par mois.'
    elif s['n_prix'] > 1:
        p += f' Les tarifs vont de {eur(mois_eur(s["mini"]))} à {eur(mois_eur(s["maxi"]))} par mois.'
    return p + '</p>'


def compare(med, ref, mot_ref):
    """Phrase de comparaison, seulement si les deux médianes existent."""
    if not (med and ref) or abs(med - ref) < 0.01: return ''
    e = 100 * (med - ref) / ref
    if abs(e) < 1.5: return f' C’est un niveau comparable à {mot_ref}.'
    sens = 'plus élevé' if e > 0 else 'moins élevé'
    return f' C’est {nb(abs(e), 0)} % {sens} que {mot_ref}.'


def bloc_statuts(s):
    t = s['public'] + s['assoc'] + s['prive']
    if not t: return ''
    p = lambda x: f' ({nb(100 * x / t, 0)} %)' if t > 3 else ''
    inconnu = s['n'] - t
    parts = []
    if s['public']: parts.append(f'<b>{s["public"]}</b> établissement{"s" if s["public"] > 1 else ""} public{"s" if s["public"] > 1 else ""}{p(s["public"])}')
    if s['assoc']: parts.append(f'<b>{s["assoc"]}</b> associatif{"s" if s["assoc"] > 1 else ""}, à but non lucratif{p(s["assoc"])}')
    if s['prive']: parts.append(f'<b>{s["prive"]}</b> privé{"s" if s["prive"] > 1 else ""} commercia{"ux" if s["prive"] > 1 else "l"}{p(s["prive"])}')
    liste = ', '.join(parts[:-1]) + (' et ' + parts[-1] if len(parts) > 1 else parts[0])
    fin = ''
    reste = (f' Le statut de {inconnu} autre{"s" if inconnu > 1 else ""} établissement{"s" if inconnu > 1 else ""} '
             f'n’est pas publié.') if inconnu > 0 else ''
    return f'<p>Répartition&nbsp;: {liste}.{reste}{fin}</p>'


def bloc_statut_prix(lot, ou):
    """Écart de tarif entre statuts, calculé sur le territoire — l'argument général « le public est
    moins cher » remplacé par les chiffres du lieu. Un statut n'est cité qu'à partir de 2 tarifs."""
    lib = {0: 'public', 1: 'associatif', 2: 'privé commercial'}
    m = {}
    for k in (0, 1, 2):
        p = [r['p'] for r in lot if r['p'] and r['statut'] == k]
        if len(p) >= 2: m[k] = (mediane(p), len(p))
    if len(m) < 2: return ''
    parts = [f'{lib[k]}&nbsp;: <b>{eur(mois_eur(v[0]))}</b> ({v[1]})' for k, v in sorted(m.items())]
    lo, hi = min(m.values()), max(m.values())
    return (f'<p><b>Tarif médian par statut {ou}</b>&nbsp;: ' + ' ; '.join(parts)
            + f'. Écart entre le statut le moins cher et le plus cher&nbsp;: {eur(mois_eur(hi[0] - lo[0]))} par mois.</p>')


def _lien_sur(ctx, r):
    """Nom de l'établissement, lié à sa fiche ou à la page de sa commune quand l'une existe ;
    sans lien sinon (commune sans page et établissement sans fiche : pas de lien mort)."""
    u = ctx['url_fiche'].get(r['fin'])
    if not u and r['cle'] in ctx['villes_page']: u = ctx['url_ville'][r['cle']]
    n = esc(r['nom_aff'])
    return f'<a href="{u}">{n}</a>' if u else f'{n} <span class="muted">({esc(r["ville_nom"])})</span>'


_POP = None


def pop75(niveau, code):
    """[habitants, 75 ans et plus, 85 ans et plus] (INSEE, RP 2023), ou None. Voir insee/pop75.py."""
    global _POP
    if _POP is None:
        f = os.path.join(B, 'insee', 'pop75.json')
        _POP = json.load(open(f, encoding='utf-8')) if os.path.exists(f) else {}
    return (_POP.get(niveau) or {}).get(code)


def _taux(lot, p):
    places = sum(r['cap'] for r in lot if r.get('cap'))
    return places, (1000 * places / p[1] if p and p[1] else None)


def bloc_population(ctx, lot, ou, niveau, code, lien_dep=None):
    """Personnes de 75 et 85 ans et plus (INSEE, recensement 2023), et, à l'échelle du département
    seulement, les places d'EHPAD rapportées aux 75 ans et plus. À l'échelle d'une commune ce rapport
    trompe : un EHPAD accueille aussi les habitants des communes voisines."""
    p = pop75(niveau, code)
    if not p or not p[1]: return ''
    places, taux = _taux(lot, p)
    sans = sum(1 for r in lot if not r.get('cap'))
    txt = (f'<p>{esc(ou[:1].upper() + ou[1:])}, {nb(p[1])} habitants ont 75 ans ou plus, soit {nb(100 * p[1] / p[0], 1)}&nbsp;% '
           f'de la population, dont {nb(p[2])} ont 85 ans ou plus.</p>')
    if niveau == 'DEP':
        fr = ctx.setdefault('_taux_fr', _taux(ctx['rows'], pop75('FRANCE', 'F'))[1])
        txt += (f'<p>Les {nb(len(lot))} EHPAD recensés {ou} totalisent {nb(places)} places d’hébergement permanent, '
                f'soit <strong>{taux:.0f} places pour 1&nbsp;000 habitants de 75 ans ou plus</strong>'
                + (f' (France&nbsp;: {fr:.0f})' if fr else '') + '. '
                'Ce taux ne compte que les EHPAD&nbsp;: ni les résidences autonomie, ni les unités de soins de longue durée.'
                + (f' La capacité de {nb(sans)} établissement{"s" if sans > 1 else ""} n’est pas connue.' if sans else '') + '</p>')
    else:
        txt += (f'<p>Ses {nb(len(lot))} EHPAD totalisent {nb(places)} places d’hébergement permanent. Ils accueillent aussi '
                'des habitants des communes voisines&nbsp;: rapporter ces places aux seuls habitants de la commune '
                'n’aurait pas de sens. Le taux d’équipement se lit à l’échelle du département'
                + (f'&nbsp;: <a href="{lien_dep}#population">voir la page du département</a>.' if lien_dep else '.') + '</p>')
    return (f'<section id="population"><h2>Les personnes âgées {ou}</h2>{txt}'
            '<p class="muted">Sources&nbsp;: INSEE, recensement de la population 2023 (population au 1<sup>er</sup> janvier 2023)&nbsp;; '
            'places installées&nbsp;: répertoire FINESS (Agence du numérique en santé), extraction du 29/09/2026.</p></section>')


def bloc_specialise(ctx, lot, ou):
    """Unités Alzheimer, UHR, PASA, hébergement temporaire et accueil de jour, d'après le répertoire
    FINESS+ (ANS, places installées au 29/09/2026). Seuls les établissements concernés sont listés."""
    avec = sorted((r for r in lot if r.get('alz') or r.get('uhr') or r.get('pasa') or r.get('ht') or r.get('aj')),
                  key=lambda r: r['nom_aff'])
    if not avec: return ''
    n_alz = sum(1 for r in lot if r.get('alz') or r.get('uhr'))
    n_ht = sum(1 for r in lot if r.get('ht')); n_aj = sum(1 for r in lot if r.get('aj'))
    n_pasa = sum(1 for r in lot if r.get('pasa'))
    cel = lambda v: f'{v}' if v else '—'
    lignes = ''.join(
        f'<tr><td>{_lien_sur(ctx, r)}</td>'
        f'<td class="num" data-l="Unité Alzheimer">{cel(r.get("alz"))}</td>'
        f'<td class="num" data-l="UHR">{cel(r.get("uhr"))}</td>'
        f'<td data-l="PASA">{"Oui" if r.get("pasa") else "—"}</td>'
        f'<td class="num" data-l="Hébergement temporaire">{cel(r.get("ht"))}</td>'
        f'<td class="num" data-l="Accueil de jour">{cel(r.get("aj"))}</td></tr>' for r in avec)
    return f"""<section id="unites-specialisees"><h2>Unités Alzheimer et accueil temporaire {ou}</h2>
<p>{nb(n_alz)} établissement{'s' if n_alz > 1 else ''} sur {nb(len(lot))} déclare{'nt' if n_alz > 1 else ''} une unité protégée
Alzheimer ou une unité d’hébergement renforcée, {nb(n_pasa)} un pôle d’activités et de soins adaptés,
{nb(n_ht)} de l’hébergement temporaire et {nb(n_aj)} un accueil de jour. Ces places existent&nbsp;; le répertoire
ne dit pas si elles sont libres.</p>
<div class="tbl-wrap"><table class="tbl"><caption>Places installées selon le répertoire FINESS (septembre 2026)</caption>
<thead><tr><th>Établissement</th><th class="num">Unité Alzheimer</th><th class="num">UHR</th><th>PASA</th><th class="num">Hébergement temporaire</th><th class="num">Accueil de jour</th></tr></thead>
<tbody>{lignes}</tbody></table></div>
<p><a href="/guides/ehpad-alzheimer-unite-protegee/">Unité protégée, UHR, PASA&nbsp;: ce qui les distingue</a> · <a href="/ehpad-alzheimer/">Les unités Alzheimer, département par département</a></p></section>"""


def bloc_has(lot, ou):
    c = collections.Counter(r['hasN'] for r in lot if r['hasN'])
    n = sum(c.values())
    if not n: return f'<p>Aucune évaluation de la Haute Autorité de santé publiée {ou} à ce jour.</p>'
    det = ', '.join(f'{k}&nbsp;: {c[k]}' for k in 'ABCD' if c.get(k))
    return (f'<p><b>Évaluations publiées {ou}</b>&nbsp;: {n} sur {len(lot)} établissements ({det}). '
            f'<a href="/guides/lire-une-evaluation-ehpad/">Lire une évaluation</a></p>')


def bloc_hausses(ctx, lot, ou):
    """Classement sur un seul critère, écrit en toutes lettres : la hausse du tarif d'hébergement entre
    2018 et 2025, pour les seuls établissements dont les deux années sont connues (comparabilité)."""
    c = [r for r in lot if r.get('serie') and r['serie'].get('d') == '2018' and r['serie'].get('f') == '2025'
         and r['fin'] in ctx['url_fiche']]
    if len(c) < 10: return ''
    c.sort(key=lambda r: r['serie']['e'])
    lig = ''.join(f'<tr><td><a href="{ctx["url_fiche"][r["fin"]]}">{esc(r["nom_aff"])}</a></td>'
                  f'<td data-l="Commune">{esc(r["ville_nom"])}</td>'
                  f'<td class="num" data-l="2018">{eur(mois_eur(r["serie"]["p"][0]))}</td>'
                  f'<td class="num" data-l="2025">{eur(mois_eur(r["serie"]["p"][-1]))}</td>'
                  f'<td class="num" data-l="Hausse">{pct(r["serie"]["e"])}</td></tr>' for r in c[:10])
    return (f'<section><h2>Les dix plus faibles hausses de tarif {esc(ou)} depuis 2018</h2>'
            f'<p>Critère unique&nbsp;: la hausse du tarif d’hébergement entre 2018 et 2025, sur les {len(c)} établissements '
            f'dont les deux tarifs sont connus. Un tarif stable peut aussi traduire un établissement habilité dont le prix est '
            f'fixé par le département.</p><div class="tbl-wrap"><table class="tbl"><caption>Tarif mensuel en 2018 et en 2025, chambre seule</caption>'
            f'<thead><tr><th>Établissement</th><th>Commune</th><th class="num">2018</th><th class="num">2025</th><th class="num">Hausse</th></tr></thead>'
            f'<tbody>{lig}</tbody></table></div></section>')


def liens_aides(lien):
    return (f'<section><h2>Réduire la facture</h2><ul class="aides-l">'
            f'<li><a href="/aides-ehpad/apa/">Allocation personnalisée d’autonomie</a> — tarif dépendance</li>'
            f'<li><a href="/aides-ehpad/aide-au-logement/">Aide au logement</a> — établissements conventionnés</li>'
            f'<li><a href="/aides-ehpad/reduction-impot/">Réduction d’impôt</a> — l’année suivante</li>'
            f'<li><a href="/aides-ehpad/aide-sociale-hebergement/">Aide sociale à l’hébergement</a> — en dernier recours</li></ul>'
            f'{cta(lien, "Estimer mon reste à charge", "seo_financement_to_calculator")}</section>')


def bloc_ash_dep(code):
    """Ce que le département fait de l'aide sociale à l'hébergement — donnée d'enquête 2018."""
    a = ASH.get(ASH_CODE.get(code, code))
    b = BAD.get(code) or {}
    out = []
    if b.get('places'):
        p = [f'<b>{nb(b["places"])}</b> places installées']
        if b.get('pct_ash') is not None:
            p.append(f'dont <b>{nb(b["pct_ash"], 1)} %</b> habilitées à l’aide sociale')
        if b.get('etp_par_resident'):
            p.append(f'<b>{nb(b["etp_par_resident"], 3).replace(",", ",")}</b> professionnel en équivalent temps plein par résident')
        out.append('<p>' + ', '.join(p) + '. <span class="src-bloc" style="border:0;padding:0;margin:0">(Direction de la recherche, des études, de l’évaluation et des statistiques — données 2023)</span></p>')
    if a:
        rec = {1: 'récupère toujours', 2: 'récupère parfois', 3: 'ne récupère pas'}.get(a.get('recours_succession'))
        ob = []
        if a.get('obliges_enfants') == 1: ob.append('aux enfants')
        if a.get('obliges_gendres') == 1: ob.append('aux gendres et belles-filles')
        if a.get('obliges_autres') == 1: ob.append('à d’autres proches')
        ph = []
        if rec: ph.append(f'le département {rec} les sommes versées sur la succession du résident')
        if ob: ph.append('la participation financière est demandée ' + ', '.join(ob))
        if a.get('gir56') == 1: ph.append('les frais liés à une faible perte d’autonomie sont pris en charge')
        if ph:
            out.append('<p><b>Si l’aide sociale à l’hébergement est demandée</b>&nbsp;: ' + ' ; '.join(ph) +
                       '. Cette pratique a été déclarée par le département lors de la dernière enquête nationale, en 2018&nbsp;: '
                       'c’est le règlement départemental en vigueur aujourd’hui qui fait foi. '
                       'Les petits-enfants, eux, ne sont plus sollicités pour cette aide depuis la loi du 8 avril 2024.</p>')
    return ''.join(out)


def bloc_evolution(s, lieu):
    if not s['evol_med'] or s['n_evol'] < 5: return ''
    e = s['evol_med']
    comp = ('plus vite que l’inflation' if e > INFL else 'moins vite que l’inflation') if abs(e - INFL) > 1 else 'au même rythme que l’inflation'
    return (f'<p><b>Évolution.</b> Entre 2018 et 2025, la hausse médiane du tarif d’hébergement, mesurée '
            f'établissement par établissement, est de <b>{pct(e)}</b> {lieu} (calcul sur {s["n_evol"]} établissements '
            f'dont le tarif est connu à deux dates au moins). Sur la même période, les prix à la consommation ont '
            f'augmenté de 17,2 % en France&nbsp;: les tarifs ont donc progressé {comp}.</p>')


# ------------------------------------------------------------------- France
def hub(ctx, ecrire):
    s = ctx['FR']
    regions = []
    for rs, (rn, deps) in geo.REGIONS.items():
        lot = [r for d in deps for r in ctx['par_dep'].get(d, [])]
        if lot: regions.append((rn, rs, stats(lot)))
    regions.sort(key=lambda x: -x[2]['n'])

    corps = f"""<h1 class="p-h1">Les EHPAD en France&nbsp;: prix, aides et reste à charge</h1>
<p class="p-sub">Un EHPAD est une maison de retraite médicalisée, pour les personnes âgées qui ne peuvent plus vivre seules chez elles. Le prix affiché n’est presque jamais ce que la famille paie réellement&nbsp;: cette page, et toutes celles qui en dépendent, servent à comprendre l’écart.</p>
<p class="p-maj">Données mises à jour le {MAJ} · {nb(s['n'])} établissements recensés</p>
{kpis([(nb(s['n']), 'EHPAD recensés en France', True),
       (med_mois(s) + '<small style="font-size:.8rem;font-weight:400">/mois</small>', 'tarif d’hébergement médian'),
       (nb(s['ash']), 'habilités à l’aide sociale'),
       (pct(s['evol_med']), 'hausse médiane du tarif depuis 2018')])}
{cta('/', 'Estimer mon reste à charge', 'seo_hub_to_calculator', 'Gratuit, sans inscription, et le calcul reste sur votre appareil.')}

<section><h2>Chercher par région</h2>
<div class="tbl-wrap"><table class="tbl"><caption>Tarif d’hébergement médian par région, en euros par mois</caption>
<thead><tr><th>Région</th><th class="num">EHPAD</th><th class="num">Tarif médian</th><th class="num">Aide sociale</th></tr></thead><tbody>
{''.join(f'<tr><td><a href="{ctx["url_region"][rs]}">{esc(rn)}</a></td>'
         f'<td class="num" data-l="EHPAD">{st["n"]}</td>'
         f'<td class="num" data-l="Tarif médian">{med_mois(st)}</td>'
         f'<td class="num" data-l="Habilités à l’aide sociale">{st["ash"]}</td></tr>' for rn, rs, st in regions)}
</tbody></table></div>
<p><b>Outre-mer</b>&nbsp;: {' · '.join(f'<a href="{ctx["url_dep"][d]}">{esc(geo.DEPARTEMENTS[d])}</a>' for d in ('971', '972', '973', '974', '975', '976') if d in ctx['url_dep'] and d in ctx['par_dep'])}</p></section>

<section><h2>Comprendre le coût</h2>
<div class="liens-grid">
<a class="lien-c" href="/prix-ehpad/"><b>Le prix des EHPAD en France</b><span>Ce que recouvre la facture, et pourquoi elle varie autant.</span></a>
<a class="lien-c" href="/prix-ehpad-par-departement/"><b>Le prix par département</b><span>Les 101 départements classés par tarif médian.</span></a>
<a class="lien-c" href="/ehpad-les-moins-chers/"><b>Les EHPAD les moins chers</b><span>Classement par tarif déclaré, département par département.</span></a>
<a class="lien-c" href="/aides-ehpad/"><b>Les aides financières</b><span>Les quatre aides qui réduisent la facture, et l’ordre dans lequel les demander.</span></a>
<a class="lien-c" href="/calcul-reste-a-charge-ehpad/"><b>Calculer le reste à charge</b><span>La méthode, ligne par ligne, avec un exemple chiffré.</span></a>
<a class="lien-c" href="/guides/"><b>Les guides</b><span>Choisir, visiter, déposer un dossier, financer.</span></a>
</div></section>
{sources()}"""
    ariane = [('Accueil', '/'), ('Les EHPAD en France', None)]
    ecrire('/ehpad/', layout.page('/ehpad/', 'Les EHPAD en France : prix, aides et reste à charge',
        f"Les {nb(s['n'])} EHPAD de France : tarif d’hébergement médian, aides mobilisables et estimation du reste à charge réel, région par région.",
        corps, ariane, type_page='hub'), 0.9, 'pages')


# ------------------------------------------------------------------- région
def region(ctx, ecrire, rs, rn, deps):
    lot = [r for d in deps for r in ctx['par_dep'].get(d, [])]
    if not lot: return
    s, FR = stats(lot), ctx['FR']
    lignes = []
    for d in sorted(deps, key=lambda d: geo.DEPARTEMENTS[d]):
        sub = ctx['par_dep'].get(d)
        if not sub: continue
        sd = stats(sub)
        lignes.append(f'<tr><td><a href="{ctx["url_dep"][d]}">{esc(geo.DEPARTEMENTS[d])} ({d})</a></td>'
                      f'<td class="num" data-l="EHPAD">{sd["n"]}</td>'
                      f'<td class="num" data-l="Tarif médian">{med_mois(sd)}</td>'
                      f'<td class="num" data-l="Habilités à l’aide sociale">{sd["ash"]}</td></tr>')
    corps = f"""<h1 class="p-h1">EHPAD {esc(phrase_region(rs, rn))}&nbsp;: prix et comparaison</h1>
<p class="p-sub">{nb(s['n'])} établissements recensés {esc(phrase_region(rs, rn))}. Comparez les tarifs département par département, puis estimez ce qui resterait réellement à payer.</p>
<p class="p-maj">Tarifs déclarés à la Caisse nationale de solidarité pour l’autonomie · {CNSA_MAJ}</p>
{kpis([(nb(s['n']), 'EHPAD recensés', True),
       (med_mois(s), 'tarif d’hébergement médian, par mois'),
       (eur(mois_eur(s['mini'])), 'tarif le plus bas'),
       (nb(s['ash']), 'habilités à l’aide sociale')])}
{phrase_prix(s, esc(phrase_region(rs, rn)), FR['med'], 'la médiane française')}
{bloc_evolution(s, phrase_region(rs, rn))}
{bloc_statut_prix(lot, esc(phrase_region(rs, rn)))}
{bloc_has(lot, esc(phrase_region(rs, rn)))}
{cta('/', 'Trouver un EHPAD adapté à ma situation', 'seo_region_to_configurator')}

<section><h2>Les départements de la région</h2>
<div class="tbl-wrap"><table class="tbl"><caption>Nombre d’EHPAD et tarif d’hébergement médian mensuel</caption>
<thead><tr><th>Département</th><th class="num">EHPAD</th><th class="num">Tarif médian</th><th class="num">Aide sociale</th></tr></thead>
<tbody>{''.join(lignes)}</tbody></table></div></section>
{sources()}"""
    ariane = [('Accueil', '/'), ('Les EHPAD en France', '/ehpad/'), (rn, None)]
    ecrire(ctx['url_region'][rs], layout.page(ctx['url_region'][rs],
        titre_court([f'EHPAD {phrase_region(rs, rn)} : prix de {nb(s["n"])} établissements',
                     f'EHPAD {phrase_region(rs, rn)} : prix et tarifs']),
        desc_courte([f'{nb(s["n"])} EHPAD {phrase_region(rs, rn)}, tarif médian {med_mois(s)} par mois.',
                     f'Hausse médiane {pct(s["evol_med"])} depuis 2018.' if s['evol_med'] else '',
                     f'{nb(s["ash"])} habilités à l’aide sociale.', 'Comparaison par département.']),
        corps, ariane, type_page='region', lieu=rn), 0.7, 'territoires')


# --------------------------------------------------------------- département
def departement(ctx, ecrire, d):
    lot = ctx['par_dep'][d]
    s, FR = stats(lot), ctx['FR']
    dn, ou = geo.DEPARTEMENTS[d], phrase_dep(d)
    rs, rn = geo.region_de(d)

    # villes du département
    villes = collections.Counter(r['cle'] for r in lot)
    avec_page = [(c, k) for c, k in villes.items() if c in ctx['villes_page']]
    avec_page.sort(key=lambda x: -x[1])
    lignes_v = []
    for c, k in avec_page[:40]:
        sv = stats(ctx['par_ville'][c])
        lignes_v.append(f'<tr><td><a href="{ctx["url_ville"][c]}">{esc(ctx["nom_ville"][c])}</a></td>'
                        f'<td class="num" data-l="EHPAD">{k}</td>'
                        f'<td class="num" data-l="Tarif médian">{med_mois(sv)}</td>'
                        f'<td class="num" data-l="Habilités à l’aide sociale">{sv["ash"]}</td></tr>')
    autres = [c for c, k in villes.items() if c not in ctx['villes_page']]
    bloc_autres = ''
    if autres:
        etabs = [r for r in lot if r['cle'] in set(autres) and r['fin'] in ctx['url_fiche']]
        etabs.sort(key=lambda r: r['ville_nom'])
        if etabs:
            bloc_autres = (f'<h3>Les autres communes du département</h3>'
                           f'<p>{len(autres)} communes {ou} comptent un seul EHPAD. Elles n’ont pas de page dédiée&nbsp;: '
                           f'la fiche de l’établissement dit tout ce que la page de commune dirait.</p><div class="puces">'
                           + ''.join(f'<a href="{ctx["url_fiche"][r["fin"]]}">{esc(r["ville_nom"])}</a>' for r in etabs[:120])
                           + '</div>')

    moins_chers = sorted([r for r in lot if r['p'] and r['fin'] in ctx['url_fiche']], key=lambda r: r['p'])[:10]
    # FAQ retirée (29/09/2026) : ses réponses répétaient la page, et Google n'affiche plus
    # les résultats enrichis FAQ depuis le 07/05/2026.
    q = ('', None)
    corps = f"""<h1 class="p-h1">EHPAD {esc(ou)}&nbsp;: prix des {nb(s['n'])} établissements</h1>
<p class="p-sub">{nb(s['n'])} établissements, dont {nb(s['ash'])} habilités à l’aide sociale{f" ; tarifs de {eur(mois_eur(s['mini']))} à {eur(mois_eur(s['maxi']))} par mois" if s['mini'] else ''}.</p>
<p class="p-maj">Tarifs déclarés à la Caisse nationale de solidarité pour l’autonomie · {CNSA_MAJ}</p>
{kpis([(nb(s['n']), 'EHPAD recensés', True),
       (med_mois(s), 'tarif d’hébergement médian, par mois'),
       (eur(mois_eur(s['mini'])), 'tarif le plus bas'),
       (nb(s['ash']), 'habilités à l’aide sociale')])}
{phrase_prix(s, esc(ou), FR['med'], 'la médiane française')}
{bloc_statuts(s)}
{bloc_statut_prix(lot, esc(ou))}
{bloc_evolution(s, ou)}
{bloc_has(lot, esc(ou))}
{bloc_population(ctx, lot, esc(ou), 'DEP', d)}
{bloc_specialise(ctx, lot, esc(ou))}
{cta('/', 'Trouver un EHPAD adapté à ma situation', 'seo_dept_to_configurator')}

<section><h2>Les villes {esc(ou)}</h2>
{'<div class="tbl-wrap"><table class="tbl"><caption>Communes comptant au moins deux EHPAD, de la plus équipée à la moins équipée</caption><thead><tr><th>Commune</th><th class="num">EHPAD</th><th class="num">Tarif médian</th><th class="num">Aide sociale</th></tr></thead><tbody>' + ''.join(lignes_v) + '</tbody></table></div>' if lignes_v else ''}
{bloc_autres}</section>

<section><h2>Les dix EHPAD au tarif le plus bas {esc(ou)}</h2>
<p>Classement sur le seul tarif d’hébergement déclaré (chambre seule).</p>
{tableau(moins_chers, ctx['lien_de'], 'Tarif d’hébergement mensuel, du plus bas au plus élevé', avec_ville=True)}</section>

{bloc_hausses(ctx, lot, ou)}

<section><h2>L’aide sociale {esc(ou)}</h2>
{bloc_ash_dep(d) or '<p>Les pratiques de ce département en matière d’aide sociale à l’hébergement n’ont pas été publiées.</p>'}
<p><a href="/aides-ehpad/aide-sociale-hebergement/">Comment fonctionne l’aide sociale à l’hébergement</a></p></section>
{q[0]}
<section><h2>Voir aussi</h2><div class="liens-grid">
{f'<a class="lien-c" href="{ctx["url_region"][rs]}"><b>Les EHPAD en {esc(rn)}</b><span>Les tarifs des départements voisins.</span></a>' if rs else ''}
<a class="lien-c" href="/prix-ehpad-par-departement/"><b>Le prix des EHPAD par département</b><span>Les 101 départements classés par tarif médian.</span></a>
<a class="lien-c" href="/aides-ehpad/"><b>Les aides financières</b><span>Ce qui réduit la facture, et dans quel ordre le demander.</span></a>
<a class="lien-c" href="/comparer-devis-ehpad/"><b>Comparer ses devis</b><span>Poste par poste, ce qui est inclus ou facturé en plus.</span></a>
</div></section>
{sources()}"""
    ariane = [('Accueil', '/'), ('Les EHPAD en France', '/ehpad/')]
    if rs: ariane.append((rn, ctx['url_region'][rs]))
    ariane.append((dn, None))
    ecrire(ctx['url_dep'][d], layout.page(ctx['url_dep'][d],
        titre_court([f'EHPAD {ou} ({d}) : prix des {nb(s["n"])} établissements',
                     f'EHPAD {ou} : prix des {nb(s["n"])} établissements', f'EHPAD {ou} : prix et tarifs']),
        desc_courte([f'{nb(s["n"])} EHPAD {ou} : tarif médian {med_mois(s)} par mois' + (f', de {eur(mois_eur(s["mini"]))} à {eur(mois_eur(s["maxi"]))}.' if s['mini'] else '.'),
                     f'Hausse médiane {pct(s["evol_med"])} depuis 2018.' if s['evol_med'] else '',
                     f'{nb(s["ash"])} habilités à l’aide sociale.', 'Comparaison par ville.']),
        corps, ariane, ld_extra=[q[1]] if q[1] else None, type_page='departement', lieu=dn), 0.8, 'territoires')


# --------------------------------------------------------------------- ville
def ville(ctx, ecrire, c):
    lot = ctx['par_ville'][c]
    s = stats(lot)
    d = lot[0]['dep']
    sd, FR = stats(ctx['par_dep'][d]), ctx['FR']
    vn, dn = ctx['nom_ville'][c], geo.DEPARTEMENTS[d]
    rs, rn = geo.region_de(d)
    cp = collections.Counter(r['cp'] for r in lot).most_common(1)[0][0]
    lien = lien_calc(cp=cp, insee=lot[0]['insee'], rayon=20)
    fusion = ctx['url_dep'][d] == ctx['url_ville'][c]   # Paris : la commune est aussi le département

    # communes voisines ayant une page
    voisines = []
    if lot[0]['lat']:
        for c2 in ctx['villes_page']:
            if c2 == c: continue
            l2 = ctx['par_ville'][c2]
            if l2[0]['dep'] != d or not l2[0]['lat']: continue
            dd = ((lot[0]['lat'] - l2[0]['lat']) * 111) ** 2 + ((lot[0]['lon'] - l2[0]['lon']) * 78) ** 2
            voisines.append((dd, c2))
        voisines.sort()
    liens_v = ''.join(f'<a href="{ctx["url_ville"][c2]}">{esc(ctx["nom_ville"][c2])}</a>' for _, c2 in voisines[:12])

    arr = ''
    if c in ('75056', '69123', '13055'):
        par_arr = collections.Counter(r['ville_nom'] for r in lot)
        arr = ('<p>Les établissements sont répartis dans les arrondissements&nbsp;: '
               + ', '.join(f'{esc(a)} ({k})' for a, k in sorted(par_arr.items())) + '.</p>')

    # FAQ retirée (29/09/2026) : ses réponses répétaient la page, et Google n'affiche plus
    # les résultats enrichis FAQ depuis le 07/05/2026.
    q = ('', None)

    bloc_aide_locale = ('<section><h2>L’aide sociale ' + esc(phrase_dep(d)) + '</h2>' + bloc_ash_dep(d) +
                        '<p><a href="/aides-ehpad/aide-sociale-hebergement/">Comment fonctionne l’aide sociale à l’hébergement</a></p></section>') if fusion and bloc_ash_dep(d) else ''
    corps = f"""<h1 class="p-h1">EHPAD à {esc(vn)}&nbsp;: prix et établissements</h1>
<p class="p-sub">{nb(s['n'])} établissements à {esc(vn)}{'' if fusion else ' (' + esc(dn) + ')'}, dont {nb(s['ash'])} habilité{'s' if s['ash'] > 1 else ''} à l’aide sociale{f" ; tarifs de {eur(mois_eur(s['mini']))} à {eur(mois_eur(s['maxi']))} par mois" if s['mini'] and s['n_prix'] > 1 else ''}.</p>
<p class="p-maj">Tarifs déclarés à la Caisse nationale de solidarité pour l’autonomie · {CNSA_MAJ}</p>
{kpis([(nb(s['n']), f'EHPAD à {esc(vn)}', True)]
      + ([(med_mois(s), 'tarif d’hébergement médian, par mois'),
          (eur(mois_eur(s['mini'])), 'tarif le plus bas')] if s['med'] else
         [('—', 'aucun tarif déclaré à ce jour')])
      + [(nb(s['ash']), 'habilités à l’aide sociale')])}
{cta(lien, 'Trouver un EHPAD adapté à ma situation', 'seo_city_to_configurator')}

<section><h2>Comparer les EHPAD à {esc(vn)}</h2>
{tableau(lot, ctx['lien_de'], 'Tarif d’hébergement mensuel pour une chambre seule, du plus bas au plus élevé, et son évolution', evol=True)}
{arr}</section>

<section><h2>Combien coûte un EHPAD à {esc(vn)}&nbsp;?</h2>
{phrase_prix(s, 'à ' + esc(vn), None if fusion else sd['med'], f'la médiane {phrase_dep(d)}')}
{bloc_statuts(s)}
{bloc_statut_prix(lot, 'à ' + esc(vn))}
{bloc_evolution(s, 'à ' + esc(vn))}
{bloc_has(lot, 'à ' + esc(vn))}</section>
{bloc_population(ctx, lot, 'à ' + esc(vn), 'DEP' if fusion else 'COM', d if fusion else c, None if fusion else ctx['url_dep'][d])}
{bloc_specialise(ctx, lot, 'à ' + esc(vn))}

{liens_aides(lien)}
{guides_tournants(c, 4)}

{bloc_aide_locale}
<section><h2>Autour de {esc(vn)}</h2>
{f'<p>Les communes voisines du même département qui comptent plusieurs EHPAD&nbsp;:</p><div class="puces">{liens_v}</div>' if liens_v else ''}
<div class="liens-grid">
{'' if fusion else f'<a class="lien-c" href="{ctx["url_dep"][d]}"><b>Tous les EHPAD {esc(phrase_dep(d))}</b><span>{nb(sd["n"])} établissements, tarif médian {med_mois(sd)} par mois.</span></a>'}
{f'<a class="lien-c" href="{ctx["url_region"][rs]}"><b>Les EHPAD {esc(phrase_region(rs, rn))}</b><span>Comparer les départements de la région.</span></a>' if rs else ''}
<a class="lien-c" href="/calcul-reste-a-charge-ehpad/"><b>Calculer le reste à charge</b><span>La méthode complète, avec un exemple chiffré.</span></a>
<a class="lien-c" href="/comparer-devis-ehpad/"><b>Comparer ses devis</b><span>Ce que chaque établissement inclut ou facture en plus, poste par poste.</span></a>
</div></section>
{sources()}"""
    ariane = [('Accueil', '/'), ('Les EHPAD en France', '/ehpad/')]
    if rs: ariane.append((rn, ctx['url_region'][rs]))
    if not fusion: ariane.append((dn, ctx['url_dep'][d]))
    ariane.append((vn, None))
    ecrire(ctx['url_ville'][c], layout.page(ctx['url_ville'][c],
        titre_court(([f'EHPAD à {vn} ({d}) : prix des {nb(s["n"])} établissements', f'EHPAD à {vn} ({d}) : prix et tarifs']
                     if ctx['slug_ville'][c] != slug(vn) and c != '75056' else [])
                    + [f'EHPAD à {vn} : prix des {nb(s["n"])} établissements', f'EHPAD à {vn} : prix et tarifs', f'EHPAD à {vn}']),
        desc_courte([f'{nb(s["n"])} EHPAD à {vn}' + (f' : tarif médian {med_mois(s)} par mois.' if s['med'] else ' : aucun tarif déclaré.'),
                     f'De {eur(mois_eur(s["mini"]))} à {eur(mois_eur(s["maxi"]))}.' if s['n_prix'] > 1 else '',
                     f'{nb(s["ash"])} habilité{"s" if s["ash"] > 1 else ""} à l’aide sociale.',
                     f'Hausse médiane {pct(s["evol_med"])} depuis 2018.' if s['evol_med'] else '',
                     'Reste à charge estimé.']),
        corps, ariane, ld_extra=[q[1]] if q[1] else None, type_page='ville', lieu=vn), 0.8, 'villes')


def page_alzheimer(ctx, ecrire):
    """Une page nationale, pas une page par ville : les sections « unités Alzheimer » des pages
    départements et villes portent le détail. Cinq cents pages quasi identiques seraient du
    contenu produit en masse."""
    rows = [r for l in ctx['par_dep'].values() for r in l]
    n_alz = sum(1 for r in rows if r.get('alz')); p_alz = sum(r.get('alz') or 0 for r in rows)
    n_uhr = sum(1 for r in rows if r.get('uhr')); p_uhr = sum(r.get('uhr') or 0 for r in rows)
    n_pasa = sum(1 for r in rows if r.get('pasa'))
    lignes = []
    for d in sorted(ctx['par_dep'], key=lambda d: geo.DEPARTEMENTS[d]):
        lot = ctx['par_dep'][d]
        a = sum(1 for r in lot if r.get('alz')); u = sum(1 for r in lot if r.get('uhr')); pa = sum(1 for r in lot if r.get('pasa'))
        pl = sum(r.get('alz') or 0 for r in lot)
        url = ctx['url_dep'][d]
        lignes.append(f'<tr><td><a href="{url}#unites-specialisees">{esc(geo.DEPARTEMENTS[d])} ({d})</a></td>'
                      f'<td class="num" data-l="EHPAD">{len(lot)}</td><td class="num" data-l="Avec unité Alzheimer">{a}</td>'
                      f'<td class="num" data-l="Places">{pl}</td><td class="num" data-l="UHR">{u}</td><td class="num" data-l="PASA">{pa}</td></tr>')
    corps = f"""<h1 class="p-h1">EHPAD avec unité Alzheimer, département par département</h1>
<p class="p-sub">{nb(n_alz)} EHPAD déclarent une unité protégée pour les personnes atteintes de la maladie
d’Alzheimer ou d’une maladie apparentée ({nb(p_alz)} places), {nb(n_uhr)} une unité d’hébergement renforcée et
{nb(n_pasa)} un pôle d’activités et de soins adaptés.</p>
<p class="p-maj">Répertoire FINESS de l’Agence du numérique en santé, places installées au 29/09/2026</p>
{kpis([(nb(n_alz), 'EHPAD avec une unité protégée', True), (nb(p_alz), 'places en unité protégée'),
       (nb(n_uhr), 'avec une UHR (' + nb(p_uhr) + ' places)'), (nb(n_pasa), 'avec un PASA')])}
<section><h2>Trois dispositifs à ne pas confondre</h2><ul>
<li><b>L’unité protégée</b>&nbsp;: une partie de l’EHPAD réservée à l’hébergement permanent de personnes
désorientées, avec des lieux conçus pour circuler sans se perdre.</li>
<li><b>L’unité d’hébergement renforcée (UHR)</b>&nbsp;: pour les troubles du comportement sévères.</li>
<li><b>Le pôle d’activités et de soins adaptés (PASA)</b>&nbsp;: un accueil en journée de résidents de l’EHPAD,
pour des activités adaptées. Il n’a pas de places propres.</li></ul>
<p><a href="/guides/ehpad-alzheimer-unite-protegee/">Le guide&nbsp;: quand une unité protégée est utile</a></p></section>
<section><h2>Par département</h2>
<div class="tbl-wrap"><table class="tbl"><caption>EHPAD déclarant une unité protégée Alzheimer, une UHR ou un PASA</caption>
<thead><tr><th>Département</th><th class="num">EHPAD</th><th class="num">Avec unité Alzheimer</th><th class="num">Places</th><th class="num">UHR</th><th class="num">PASA</th></tr></thead>
<tbody>{''.join(lignes)}</tbody></table></div>
<p>Le détail, établissement par établissement, figure sur chaque page département et chaque page ville.
Le répertoire recense les places installées, pas les places libres&nbsp;: seul l’établissement peut dire si
une place est disponible.</p></section>
{cta('/', 'Trouver un EHPAD adapté à ma situation', 'seo_alz_to_configurator')}
<p class="src-bloc"><b>Sources</b>&nbsp;: répertoire FINESS (Agence du numérique en santé, jeu « FINESS - Activités »,
Licence Ouverte 2.0, fichier du 29/09/2026) et nomenclatures officielles de l’ANS (activité, mode de fonctionnement,
clientèle). Contrôle croisé avec le référentiel Atlasanté des activités FINESS (janvier 2026).</p>"""
    ecrire('/ehpad-alzheimer/', layout.page('/ehpad-alzheimer/', 'EHPAD avec unité Alzheimer : la liste par département',
        f'{nb(n_alz)} EHPAD avec une unité protégée Alzheimer, {nb(n_uhr)} avec une UHR, {nb(n_pasa)} avec un PASA : '
        'le décompte par département, d’après le répertoire officiel FINESS.',
        corps, [('Accueil', '/'), ('Les EHPAD en France', '/ehpad/'), ('Unités Alzheimer', None)], type_page='hub'), 0.8, 'pages')


def construire(ctx, ecrire):
    hub(ctx, ecrire)
    page_alzheimer(ctx, ecrire)
    for rs, (rn, deps) in geo.REGIONS.items():
        if rs in ('guadeloupe', 'martinique', 'guyane', 'la-reunion', 'mayotte'):
            continue          # outre-mer : la région et le département se confondent, une seule page
        region(ctx, ecrire, rs, rn, deps)
    for d in sorted(ctx['par_dep']):
        if d == '75': continue   # Paris : la commune et le département se confondent, la page ville fait les deux
        departement(ctx, ecrire, d)
    for c in sorted(ctx['villes_page']):
        ville(ctx, ecrire, c)
