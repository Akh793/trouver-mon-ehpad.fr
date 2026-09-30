# -*- coding: utf-8 -*-
"""Fiche d'un établissement : ce qu'il coûte, où il se situe, ce qui reste à payer.

Règle d'écriture (audit du 29/09/2026) : une fiche ne répète pas de texte pédagogique. Chaque
paragraphe est calculé pour CET établissement : rang de prix, écart au même statut, évolution
annuelle, détail de l'évaluation, coût mensuel selon le GIR. Les explications générales vivent
dans les guides, vers lesquels la fiche renvoie par un lien. Aucun chiffre n'est écrit s'il n'est
pas calculable à partir des données publiques."""
import collections, math, statistics
import geo, layout
from base import (esc, nb, eur, eur2, pct, mois_eur, stats, mediane, lien_calc, titre, MOIS,
                  MARQUE, MAJ, CNSA_MAJ, DOMAINE, AUTEUR, AUTEUR_URL, APA_SEUIL_INF, IR_MAX, BAREME)
from pieces import cta, tableau, STATUT_LONG, guides_tournants, GUIDES_LIENS
from territoires import phrase_dep, med_mois

INFL = 17.2          # INSEE, prix à la consommation, cumul 2018 → 2025
ANNEES = ['2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025']
SOINS_COURT = {'G': 'tarif global de soins (médecins généralistes et examens courants payés par l’établissement)',
               'P': 'tarif partiel de soins (médecins et examens réglés comme à domicile)',
               'V': 'petite unité de vie'}
CHAPITRES = ('la personne accompagnée', 'les professionnels', 'l’établissement')
STATUT_PLUR = {0: 'publics', 1: 'associatifs', 2: 'privés commerciaux'}


def date_fr(iso):
    if not iso: return ''
    p = str(iso)[:10].split('-')
    return '/'.join(reversed(p)) if len(p) == 3 else str(iso)


def mois_fr(maj):
    try:
        a, m = str(maj).split('-')[:2]
        return f'{m}/{a}'
    except Exception:
        return ''


def de_l(nom):
    """« de l’EHPAD Les Tilleuls » — jamais « de l’EHPAD EHPAD Les Tilleuls »."""
    return f'de l’{nom}' if nom.upper().startswith('EHPAD') else f'de l’EHPAD {nom}'


def rang_txt(k, n):
    return '1<sup>er</sup>' if k == 1 else f'{k}<sup>e</sup>'


# --------------------------------------------------------------- blocs calculés
def bloc_couts(r):
    """Prix facturé selon le GIR, puis ce qui reste à payer dans le cas le plus fréquent."""
    if not r['p']:
        return ('<p>Aucun tarif déclaré&nbsp;: demandez-le à l’établissement.</p>'), None
    h = eur2(r['p'])
    lignes = [f'<li><b>Hébergement, chambre seule&nbsp;: {h} par jour</b>, soit {eur(mois_eur(r["p"]))} par mois'
              + (f' (tarif déclaré en {mois_fr(r["maj"])})' if r['maj'] else '') + '.</li>']
    if r['pcd']:
        lignes.append(f'<li>Chambre double&nbsp;: {eur2(r["pcd"])} par jour ({eur(mois_eur(r["pcd"]))} par mois).</li>')
    if r['pa'] and r['ash'] in (1, 2):
        e = 100 * (r['pa'] - r['p']) / r['p']
        lignes.append(f'<li>Tarif « aide sociale »&nbsp;: {eur2(r["pa"])} par jour'
                      + (f', {nb(abs(e), 0)} % {"de moins" if e < 0 else "de plus"} que le tarif courant' if abs(e) >= 0.5 else '')
                      + '.</li>')
    if r['temp'] is not None:
        lignes.append(f'<li>Accueil temporaire&nbsp;: {eur2(r["temp"])} par jour.</li>')
    out = '<ul>' + ''.join(lignes) + '</ul>'

    if r.get('reg') == 'exp':
        pf = (r.get('pf') or {}).get('montant_jour') or 0
        tot = mois_eur(r['p'] + pf)
        out += (f'<table class="tbl t-cout"><caption>Ce qui est facturé chaque mois, avant aide au logement</caption><tbody>'
                f'<tr><td>Hébergement</td><td class="num" data-l="Par mois">{eur(mois_eur(r["p"]))}</td></tr>'
                f'<tr><td>Aide au quotidien, forfait de {eur2(pf)} par jour</td>'
                f'<td class="num" data-l="Par mois">{eur(mois_eur(pf))}</td></tr>'
                f'<tr><td><b>Total</b></td><td class="num" data-l="Par mois"><b>{eur(tot)}</b></td></tr></tbody></table>'
                '<p>Ici, <a href="/aides-ehpad/apa/">l’APA est remplacée par ce forfait</a>, identique pour tous.</p>')
        return out, tot
    if not (r['t12'] and r['t56']):
        out += '<p>Tarifs dépendance non déclarés&nbsp;: coût complet à demander.</p>'
        return out, None
    rows = []
    for g, t in (('1-2', r['t12']), ('3-4', r['t34']), ('5-6', r['t56'])):
        if t: rows.append(f'<tr><td>GIR {g}</td><td class="num" data-l="Dépendance / jour">{eur2(t)}</td>'
                          f'<td class="num" data-l="Total / mois">{eur(mois_eur(r["p"] + t))}</td></tr>')
    uniq = r['t12'] and r['t56'] and abs(r['t12'] - r['t56']) < 0.01
    out += ('<table class="tbl t-cout"><caption>Prix facturé chaque mois selon le niveau de perte d’autonomie, avant aides</caption>'
            '<thead><tr><th>Niveau (GIR)</th><th class="num">Tarif dépendance / jour</th><th class="num">Hébergement + dépendance / mois</th></tr></thead>'
            '<tbody>' + ''.join(rows) + '</tbody></table>')
    if uniq:
        out += '<p>Même tarif déclaré pour tous les GIR&nbsp;: demandez celui qui s’appliquera.</p>'
    tot = mois_eur(r['p'] + r['t56'])
    return out, tot


def bloc_reste(r, tot):
    """Reste à charge du cas le plus fréquent : ressources sous le premier seuil de l'APA."""
    if not tot: return ''
    an = tot * 12
    ir = min(BAREME['irTaux'] * min(an, BAREME['irPlafond']), IR_MAX)
    if r.get('reg') == 'exp':
        tete = f'<p>Reste à payer&nbsp;: <b>{eur(tot)} par mois</b>, quelles que soient les ressources'
    else:
        tete = (f'<p>Sous {eur2(APA_SEUIL_INF)} de ressources par mois, l’APA ramène la facture à '
                f'<b>{eur(tot)} par mois</b>, quel que soit le GIR')
    return (tete + ', avant aide au logement. '
            f'Réduction d’impôt si imposable&nbsp;: jusqu’à {eur(ir)} par an. '
            f'<a href="/calcul-reste-a-charge-ehpad/">Méthode</a>.</p>')


def bloc_position(r, ctx, dp, vn, sv):
    """Où se situe ce tarif : rang dans le département, même statut, ville, France."""
    if not r['p']: return ''
    d = r['dep']
    prix = dp['prix']
    k = 1 + sum(1 for x in prix if x < r['p'] - 1e-9)
    n = len(prix)
    ph = [f'<p>{rang_txt(k, n)} tarif le plus bas sur les <b>{n}</b> EHPAD {esc(phrase_dep(d))} ayant déclaré le leur'
          + '.']
    st = r['statut']
    ms = dp['statut'].get(st)
    if st is not None and ms and ms[1] >= 3:
        e = 100 * (r['p'] - ms[0]) / ms[0]
        ph.append(f'Médiane des {ms[1]} établissements {STATUT_PLUR[st]} du département&nbsp;: {eur(mois_eur(ms[0]))}'
                  + ('.' if abs(e) < 1.5 else f' (<b>{pct(e, 0)}</b> ici).'))
    if sv and sv['med'] and sv['n_prix'] >= 3:
        e = 100 * (r['p'] - sv['med']) / sv['med']
        ph.append(f'À {esc(vn)}&nbsp;: {med_mois(sv)}' + ('.' if abs(e) < 1.5 else f' ({pct(e, 0)} ici).'))
    fr = ctx['FR']['med']
    if fr:
        e = 100 * (r['p'] - fr) / fr
        ph.append(f'France&nbsp;: {eur(mois_eur(fr))} ({pct(e, 0)} ici).')
    return ' '.join(ph) + '</p>'


def bloc_evolution(r, dp):
    s = r.get('serie')
    if not s or s.get('e') is None: return ''
    pts = [(a, v) for a, v in zip(ANNEES, s['p']) if v]
    if len(pts) < 2: return ''
    lig = []
    for i, (a, v) in enumerate(pts):
        var = ''
        if i and int(a) - int(pts[i - 1][0]) == 1:
            var = pct(100 * (v - pts[i - 1][1]) / pts[i - 1][1])
        lig.append(f'<tr><td>{a}</td><td class="num" data-l="Par jour">{eur2(v)}</td>'
                   f'<td class="num" data-l="Sur un an">{var or "—"}</td></tr>')
    t = ('<div class="tbl-wrap"><table class="tbl t-evol"><caption>Tarif d’hébergement par jour, chambre seule</caption>'
         '<thead><tr><th>Année</th><th class="num">Par jour</th><th class="num">Sur un an</th></tr></thead><tbody>'
         + ''.join(lig) + '</tbody></table></div>')
    ph = [f'<p>De <b>{eur2(pts[0][1])}</b> en {pts[0][0]} à <b>{eur2(pts[-1][1])}</b> en {pts[-1][0]}&nbsp;: '
          f'<b>{pct(s["e"])}</b>' + (f', soit {pct(s["a"], 2)} par an' if s.get('a') is not None else '') + '.']
    # plus forte variation d'une année sur l'autre (années consécutives seulement)
    sauts = [(100 * (b[1] - a[1]) / a[1], b[0]) for a, b in zip(pts, pts[1:]) if int(b[0]) - int(a[0]) == 1]
    if sauts:
        m = max(sauts, key=lambda x: abs(x[0]))
        if abs(m[0]) >= 2:
            ph.append(f'Plus forte variation annuelle&nbsp;: {pct(m[0])} en {m[1]}.')
    if s['d'] == '2018' and s['f'] == '2025':
        ph.append('Inflation&nbsp;: +17,2 %.')
    ev = dp['evol']
    if len(ev) >= 10:
        ph.append(f'Médiane {esc(phrase_dep(r["dep"]))}&nbsp;: {pct(statistics.median(ev))}.')
    return '<section><h2>L’évolution du tarif depuis ' + pts[0][0] + '</h2>' + t + ' '.join(ph) + '</p></section>'


def bloc_qualite(r, dp):
    out = []
    if r['hasN']:
        p = (f'<p><b>Note {r["hasN"]}</b> (de A à D) à l’évaluation du {date_fr(r["hasD"])}'
             + (f', réalisée par {esc(titre(r["hasO"]))}' if r['hasO'] else '') + '.')
        if r['hasM'] is not None:
            p += f' Moyenne des objectifs&nbsp;: <b>{nb(r["hasM"], 1)}/100</b>'
            if dp['hasM'] and len(dp['hasM']) >= 5:
                k = sum(1 for x in dp['hasM'] if x < r['hasM'])
                p += (f', au-dessus de {nb(100 * k / len(dp["hasM"]), 0)} % des établissements évalués '
                      f'{esc(phrase_dep(r["dep"]))}')
            p += '.'
        if r['hasCI'] is not None:
            p += f' Critères impératifs atteints&nbsp;: <b>{r["hasCI"]} sur 18</b>.'
        out.append(p + '</p>')
        if r.get('hasC') and len(r['hasC']) == 3 and all(x is not None for x in r['hasC']):
            out.append('<ul class="has-ch">' + ''.join(
                f'<li>Chapitre « {c} »&nbsp;: <b>{nb(v, 2)}/4</b></li>' for c, v in zip(CHAPITRES, r['hasC'])) + '</ul>')
    else:
        out.append('<p>Pas d’évaluation publiée par la Haute Autorité de santé à ce jour.</p>')
    if r['alim']:
        a = r['alim']
        out.append(f'<p>Hygiène alimentaire&nbsp;: <b>{esc(a[0])}</b> au contrôle du {date_fr(a[1])}'
                   + (f' (suite&nbsp;: {esc(a[2])})' if a[2] else '') + '.</p>')
    out.append(bloc_ars(r))
    out.append('<p><a href="/guides/lire-une-evaluation-ehpad/">Lire une évaluation</a></p>')
    return ''.join(out)


_ARS = None


def bloc_ars(r):
    """Documents du plan national de contrôle des EHPAD 2022-2024 publiés par l'ARS (ars/extraire_ars.py).
    Un document n'est cité que s'il porte le numéro FINESS de l'établissement ; sinon, lien vers la
    page régionale. Aucun résumé, aucune note : les constats datent du contrôle."""
    global _ARS
    if _ARS is None:
        import os, json
        f = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ars', 'ars_inspections.json')
        _ARS = json.load(open(f, encoding='utf-8')) if os.path.exists(f) else {'regions': {}, 'documents': {}}
    rs, _ = geo.region_de(r['dep'])
    reg = _ARS['regions'].get(rs)
    docs = _ARS['documents'].get(r['fin'])
    if docs:
        liens = ' · '.join(
            f'<a href="{esc(d["url"])}" rel="nofollow">{esc(d["type"])}' + (f' du {d["date"]}' if d.get('date') else '') + '</a>'
            for d in docs)
        return (f'<p>Contrôle de l’ARS 2022-2024&nbsp;: {liens} (constats à la date du contrôle).</p>')
    if not reg: return ''
    return (f'<p>Contrôles de l’ARS 2022-2024&nbsp;: <a href="{esc(reg["url"])}" rel="nofollow">page de l’ARS {esc(reg["nom"])}</a>.</p>')


def bloc_aides(r):
    ash = {1: f'<b>habilité</b>{" — tarif aide sociale " + eur2(r["pa"]) + " par jour" if r["pa"] else ""}',
           2: '<b>à confirmer</b> auprès de l’établissement',
           0: '<b>non habilité</b>'}.get(r['ash'], 'information non publiée')
    apa = ('remplacée ici par la participation forfaitaire' if r.get('reg') == 'exp'
           else 'couvre le tarif dépendance au-delà du GIR 5-6')
    return (f'<ul class="aides-l">'
            f'<li><a href="/aides-ehpad/aide-sociale-hebergement/">Aide sociale à l’hébergement</a>&nbsp;: {ash}.</li>'
            f'<li><a href="/aides-ehpad/apa/">Allocation personnalisée d’autonomie</a>&nbsp;: {apa}.</li>'
            f'<li><a href="/aides-ehpad/aide-au-logement/">Aide au logement</a> et '
            f'<a href="/aides-ehpad/reduction-impot/">réduction d’impôt</a>.</li></ul>')


def offre(r):
    """Unités et accueils déclarés au répertoire FINESS+ (places installées au 29/09/2026)."""
    p = lambda n: f'{n} place' + ('s' if n > 1 else '')
    o = []
    if r.get('alz'): o.append(f'unité protégée Alzheimer ({p(r["alz"])})')
    if r.get('uhr'): o.append(f'unité d’hébergement renforcée ({p(r["uhr"])})')
    if r.get('pasa'): o.append('pôle d’activités et de soins adaptés (PASA)')
    if r.get('ht'): o.append(f'hébergement temporaire ({p(r["ht"])})')
    if r.get('aj'): o.append(f'accueil de jour ({p(r["aj"])})')
    return o


def bloc_pratique(r):
    l = []
    l.append(f'<li>N° FINESS&nbsp;: {r["fin"]}.</li>')
    if r['statut'] is not None: l.append(f'<li>Statut&nbsp;: {STATUT_LONG[r["statut"]]}.</li>')
    if r['pm']: l.append(f'<li>Gestionnaire&nbsp;: {esc(titre(r["pm"]))}' + (f' (SIREN {r["siren"]})' if r.get('siren') else '') + '.</li>')
    if r['cap']: l.append(f'<li>{r["cap"]} places' + ('' if r.get('capsrc') == 'finess' else ' (2020)') + '.</li>')
    o = offre(r)
    if o: l.append(f'<li>Accueil spécialisé&nbsp;: {", ".join(o)}.</li>')
    if r['ouv']: l.append(f'<li>Ouvert en {esc(r["ouv"])}.</li>')
    if r['tarif'] in SOINS_COURT:
        l.append(f'<li>Soins&nbsp;: {SOINS_COURT[r["tarif"]]}' + (', pharmacie interne' if r['pui'] else '') + '.</li>')
    incl = [x.strip() for x in (r.get('inclTxt') or '').split(';') if x.strip()]
    sus = [x.strip() for x in (r.get('susTxt') or '').split(';') if x.strip()]
    if incl: l.append(f'<li>Compris dans le tarif&nbsp;: {esc(", ".join(incl))}.</li>')
    if sus: l.append(f'<li>Facturé en plus&nbsp;: {esc(", ".join(sus))}.</li>')
    if not incl and not sus and (r['nIncl'] or r['nSus']):
        l.append(f'<li>{r["nIncl"] or 0} prestation(s) comprise(s), {r["nSus"] or 0} en supplément.</li>')
    return '<ul>' + ''.join(l) + '</ul>' if l else ''


def bloc_production(r):
    """« Comment cette page est produite » : sources datées propres à la fiche + responsable."""
    s = [f'tarifs déclarés à la CNSA{" en " + mois_fr(r["maj"]) if r["maj"] else ""}',
         'identité, gestionnaire et habilitation&nbsp;: répertoire FINESS']
    if r['hasN']: s.append(f'évaluation&nbsp;: Haute Autorité de santé, {date_fr(r["hasD"])}')
    if r['alim']: s.append(f'hygiène&nbsp;: Alim’confiance, {date_fr(r["alim"][1])}')
    if r.get('serie'): s.append('historique&nbsp;: fichiers annuels CNSA 2018-2025')
    return (f'<p class="src-bloc"><b>Sources</b>&nbsp;: {"&nbsp;; ".join(s)}. Calculs automatiques. '
            f'Publication&nbsp;: <a href="{AUTEUR_URL}">{AUTEUR}</a>. '
            f'<a href="/notre-methodologie.html">Méthode</a> · '
            f'<a href="mailto:contact@trouver-mon-ehpad.fr?subject=Correction%20{r["fin"]}">Signaler une erreur</a></p>')


# --------------------------------------------------------------------- fiche
def fiche(ctx, ecrire, r, voisins, dp, freres):
    vn = ctx['nom_ville'].get(r['cle']) or r['ville_nom']
    d = r['dep']; dn = geo.DEPARTEMENTS[d]
    rs, rn = geo.region_de(d)
    sv = stats(ctx['par_ville'][r['cle']]) if r['cle'] in ctx['par_ville'] else None
    sd = dp['stats']
    lien = lien_calc(cp=r['cp'], insee=r['insee'], rayon=20, finess=r['fin'])
    url = ctx['url_fiche'][r['fin']]
    nom = r['nom_aff']

    adr = ' '.join(x for x in [titre(r['adr']) if r['adr'] else None, r['cp'], vn] if x)
    tel = r['tel']
    tel_aff = ' '.join(tel[i:i + 2] for i in range(0, len(tel), 2)) if tel else None
    statut = STATUT_LONG.get(r['statut'])
    couts, tot = bloc_couts(r)

    sous = (f'EHPAD {statut + " " if statut else ""}à {esc(vn)} ({esc(dn)})'
            + (f', géré par {esc(titre(r["pm"]))}' if r['pm'] and titre(r['pm']).lower() not in nom.lower() else '') + '.')

    vs = [x for x in voisins if x['p']]
    ecart_v = ''
    if len(vs) >= 2:
        lo, hi = min(x['p'] for x in vs), max(x['p'] for x in vs)
        ecart_v = (f'<p>Entre le moins cher et le plus cher de ces {len(vs)} voisins&nbsp;: '
                   f'<b>{eur(mois_eur(hi - lo))} par mois</b> d’écart.</p>')

    bloc_freres = ''
    if freres:
        bloc_freres = ('<section><h2>Le même gestionnaire</h2><p>' + esc(titre(r['pm'])) + ' gère aussi&nbsp;:</p><div class="puces">'
                       + ''.join(f'<a href="{ctx["url_fiche"][x["fin"]]}">{esc(x["nom_aff"])} ({esc(x["ville_nom"])})</a>' for x in freres)
                       + '</div></section>')

    corps = f"""<h1 class="p-h1">{esc(nom)}</h1>
<p class="p-sub">{sous}</p>
<div class="f-head">
<div class="f-grid">
<div><b>{eur(mois_eur(r['p'])) + '<small style="font-size:.75rem;font-weight:400">/mois</small>' if r['p'] else 'Non déclaré'}</b><span>hébergement, chambre seule</span></div>
<div><b>{r['cap'] or '—'}</b><span>places{'' if r.get('capsrc') == 'finess' else ' (2020)'}</span></div>
<div><b>{'Oui' if r['ash'] == 1 else ('À confirmer' if r['ash'] == 2 else ('Non' if r['ash'] == 0 else '—'))}</b><span>aide sociale à l’hébergement</span></div>
<div><b>{r['hasN'] or '—'}</b><span>évaluation officielle (A à D)</span></div>
</div>
<p class="f-adr">{esc(adr)}{f' · <a href="tel:{esc(tel)}">{esc(tel_aff)}</a>' if tel_aff else ''}</p>
</div>
{cta(lien, 'Estimer mon reste à charge', 'seo_establishment_to_calculator')}

<section><h2>Ce qu’il coûte</h2>
{couts}
{bloc_reste(r, tot)}</section>

{'<section><h2>Où se situe ce tarif</h2>' + bloc_position(r, ctx, dp, vn, sv) + '</section>' if r['p'] else ''}

{bloc_evolution(r, dp)}

<section><h2>Les aides</h2>
{bloc_aides(r)}</section>

<section><h2>Évaluation et contrôles</h2>
{bloc_qualite(r, dp)}</section>

<section><h2>En pratique</h2>
{bloc_pratique(r)}</section>

<section><h2>Les EHPAD à proximité</h2>
{tableau(voisins, ctx['lien_de'], 'Les plus proches ayant déclaré un tarif, du moins cher au plus cher', avec_ville=True) if voisins else '<p>Aucun autre établissement avec tarif déclaré dans les environs immédiats.</p>'}
{ecart_v}
<div class="liens-grid">
{f'<a class="lien-c" href="{ctx["url_ville"][r["cle"]]}"><b>Tous les EHPAD à {esc(vn)}</b><span>{sv["n"]} établissements, tarif médian {med_mois(sv)} par mois.</span></a>' if r['cle'] in ctx['url_ville'] and r['cle'] in ctx['villes_page'] and ctx['url_ville'][r['cle']] != ctx['url_dep'][d] else ''}
<a class="lien-c" href="{ctx['url_dep'][d]}"><b>Les EHPAD {esc(phrase_dep(d))}</b><span>{nb(sd['n'])} établissements, tarif médian {med_mois(sd)} par mois.</span></a>
<a class="lien-c" href="/comparer-devis-ehpad/"><b>Comparer ses devis</b><span>Poste par poste, avec celui d’un autre établissement.</span></a>
</div></section>
{bloc_freres}
{guides_tournants(r['fin'], 3, [GUIDES_LIENS[10]] if r['ash'] == 1 else ([GUIDES_LIENS[2]] if not r['p'] else None))}
{bloc_production(r)}"""

    ld = [{
        "@type": "WebPage", "@id": DOMAINE + url, "url": DOMAINE + url, "inLanguage": "fr-FR",
        "name": f"{nom} à {vn}",
        "isPartOf": {"@id": DOMAINE + "/#website"},
        "author": {"@id": DOMAINE + "/#editeur"}, "publisher": {"@id": DOMAINE + "/#organization"},
        "about": {"@type": "Place", "name": nom,
                  "address": {"@type": "PostalAddress", "addressLocality": vn, "postalCode": r['cp'],
                              "addressCountry": "FR", **({"streetAddress": titre(r['adr'])} if r['adr'] else {})},
                  **({"geo": {"@type": "GeoCoordinates", "latitude": r['lat'], "longitude": r['lon']}}
                     if r['lat'] and not r.get('approx') else {}),
                  **({"telephone": r['tel']} if r['tel'] else {}),
                  "identifier": {"@type": "PropertyValue", "propertyID": "FINESS", "value": r['fin']}},
    }]
    ariane = [('Accueil', '/'), ('Les EHPAD en France', '/ehpad/')]
    if rs: ariane.append((rn, ctx['url_region'][rs]))
    ariane.append((dn, ctx['url_dep'][d]))
    if r['cle'] in ctx['villes_page']: ariane.append((vn, ctx['url_ville'][r['cle']]))
    ariane.append((nom, None))

    prix = f'{eur(mois_eur(r["p"]))}/mois' if r['p'] else None
    court = r.get('nom_court') or layout.coupe_mot(nom, 58 - len(vn) - 3)
    titre_p = layout.titre_court(
        ([f'{nom} à {vn} : {prix}'] if prix else [])
        + [f'{nom} à {vn} : tarifs et aides', f'{nom} ({vn})']
        + ([f'{court} ({vn}) : {prix}'] if prix else [])
        + [f'{court} ({vn})', f'{court} ({vn})'[:60]])
    s = r.get('serie')
    desc = layout.desc_courte([
        f'{nom} à {vn}{" (" + d + ")" if len(vn) < 25 else ""} :',
        f'hébergement {prix} en chambre seule.' if prix else 'tarif non déclaré.',
        f'{pct(s["e"], 0)} depuis {s["d"]}.' if s and s.get('e') is not None else '',
        f'Évaluation HAS {r["hasN"]}.' if r['hasN'] else '',
        {1: 'Habilité à l’aide sociale.', 0: 'Non habilité à l’aide sociale.'}.get(r['ash'], ''),
        'Reste à charge estimé.' if tot else '',
    ])
    ecrire(url, layout.page(url, titre_p, desc, corps, ariane, ld_extra=ld,
                            type_page='etablissement', lieu=vn), 0.6, 'etablissements')


def construire(ctx, ecrire, liste):
    par_dep = collections.defaultdict(list)
    for r in liste: par_dep[r['dep']].append(r)
    # frères : même gestionnaire (SIREN), fiches publiées, au plus 6, les plus proches d'abord
    par_siren = collections.defaultdict(list)
    for r in liste:
        if r.get('siren') and r['fin'] in ctx['url_fiche']: par_siren[r['siren']].append(r)
    for d, lot in par_dep.items():
        tout = ctx['par_dep'][d]
        dp = {'stats': stats(tout),
              'prix': sorted(x['p'] for x in tout if x['p']),
              'evol': [x['serie']['e'] for x in tout if x.get('serie') and x['serie'].get('e') is not None],
              'hasM': [x['hasM'] for x in tout if x['hasM'] is not None],
              'statut': {}}
        for k in (0, 1, 2):
            p = [x['p'] for x in tout if x['p'] and x['statut'] == k]
            if p: dp['statut'][k] = (mediane(p), len(p))
        avec = [x for x in tout if x['p'] and x['lat'] and x['fin'] in ctx['url_fiche']]
        for r in lot:
            vois = []
            if r['lat']:
                for x in avec:
                    if x['fin'] == r['fin']: continue
                    dd = math.hypot((r['lat'] - x['lat']) * 111, (r['lon'] - x['lon']) * 111 * math.cos(math.radians(r['lat'])))
                    vois.append((dd, x))
                vois.sort(key=lambda t: t[0])
            fr = [x for x in par_siren.get(r.get('siren'), []) if x['fin'] != r['fin']]
            if r['lat']:
                fr.sort(key=lambda x: (x['lat'] is None, math.hypot(((x['lat'] or 0) - r['lat']) * 111, ((x['lon'] or 0) - r['lon']) * 78)))
            fiche(ctx, ecrire, r, [x for _, x in vois[:6]], dp, fr[:6])
