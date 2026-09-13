# -*- coding: utf-8 -*-
"""Refonte rédactionnelle — lot 4 : le résumé de fiche.

Le résumé disait trois fois le même chiffre : en gros, puis « L'établissement
facture X », puis l'écart à la médiane. Les repères mélangeaient des choses de
nature différente — une capacité qui ne dit rien des places libres, un « Non »
suivi de « accepte l'aide sociale » qui se lit de travers, un statut juridique
présenté comme « qui gère l'établissement », alors que c'est une catégorie et non
un nom de gestionnaire.

L'aide sociale reçoit un état rédigé, identique partout : l'habilitation porte sur
des places, pas sur l'établissement, et elle n'ouvre aucun droit à elle seule.
"""
import io, os, sys

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site', 'app.js')
s = io.open(P, encoding='utf-8').read()
n = 0


def rem(a, b):
    global s, n
    if a not in s:
        print('INTROUVABLE :', a[:110].replace('\n', ' '))
        sys.exit(1)
    s = s.replace(a, b, 1)
    n += 1


# ── 1. L'état de l'aide sociale, écrit une fois pour toute la fiche
rem(
    "  function fait(val, lib) { return `<div><b>${esc(val)}</b><span>${esc(lib)}</span></div>`; }",
    """  function fait(val, lib) { return `<div><b>${esc(val)}</b><span>${esc(lib)}</span></div>`; }

  /* L'habilitation à l'aide sociale porte sur un NOMBRE DE PLACES, pas sur
     l'établissement entier, et elle n'ouvre aucun droit par elle-même : le
     département décide dossier par dossier. Un « Oui » sec laisserait croire
     l'inverse. Les quatre états sont rédigés ici, et nulle part ailleurs. */
  const ASH_LIB = {
    1: 'Oui, sous conditions',
    2: 'À confirmer',
    0: 'Non',
  };
  const ASH_NOTE = {
    1: 'Certaines places sont habilitées. L’accord dépend du département et de la place proposée.',
    2: 'Le répertoire et le tarif déclaré se contredisent. À vérifier auprès de l’établissement.',
    0: 'Établissement non habilité. Une exception existe après plusieurs années de séjour payé : à voir avec le département.',
  };
  const ashEtat = (e) => (ASH_LIB[e[C.ash]] || 'Non renseigné');
  const ashNote = (e) => (ASH_NOTE[e[C.ash]] || 'Information absente du répertoire.');"""
)

# ── 2. L'en-tête : un seul montant à ce niveau, nommé
rem(
    """    const gros = !r.prixConnu ? 'Tarif non déclaré' : euro(p ? r.rac : r.total);
    const lib = !r.prixConnu ? 'l’établissement ne l’a pas communiqué à la CNSA'
      : (p ? 'à payer chaque mois, une fois les aides déduites' : 'prix affiché, avant les aides');""",
    """    const gros = !r.prixConnu ? 'Tarif non renseigné' : euro(p ? r.decaisse : r.facture) + ' / mois';
    const lib = !r.prixConnu ? 'Non communiqué par l’établissement'
      : p ? (r.depConnue ? 'Budget estimé' : 'Calcul incomplet')
          : 'Tarif avant aides';"""
)

rem(
    """        ${r.prixConnu && p ? (r.aides >= 1
          ? `<p class="ctx">L’établissement facture ${euro(r.total)} · les aides en retirent ${euro(r.aides)}</p>`
          : r.reg === 'exp'
            ? `<p class="ctx">L’établissement facture ${euro(r.total)}. Dans ce territoire, l’APA en établissement
               n’existe plus&nbsp;: elle est remplacée par la participation forfaitaire déjà comprise dans ce montant.</p>`
            : `<p class="ctx">L’établissement facture ${euro(r.total)}, et aucune aide n’a pu être déduite${r.notes.length ? ' — la raison est expliquée dans l’onglet «&nbsp;Prix &amp; aides&nbsp;»' : ''}.</p>`) : ''}
        ${r.prixConnu && !p ? `<p class="ctx">Indiquez ${mot('retraite')}, en haut de page, pour voir ce qui resterait vraiment à payer.</p>` : ''}
        ${ecartMediane(o)}""",
    """        ${r.prixConnu && p ? `<p class="ctx">${!r.depConnue
            ? 'La part «&nbsp;aide au quotidien&nbsp;» n’est pas déclarée&nbsp;: le budget réel sera plus élevé.'
            : r.aides >= 1
              ? `Aides déduites&nbsp;: ${euro(r.aides)}. Hors frais d’entrée et dépenses personnelles.`
              : r.reg === 'exp'
                ? 'Forfait d’aide au quotidien inclus. Hors frais d’entrée et dépenses personnelles.'
                : 'Aucune aide déduite au vu des ressources indiquées. Hors frais d’entrée et dépenses personnelles.'}</p>` : ''}
        ${r.prixConnu && !p ? `<p class="ctx">Indiquez ${mot('retraite')}, en haut de page, pour estimer le budget.</p>` : ''}
        ${r.prixConnu && p && r.trou > 0 ? `<p class="f-manque"><b>À compléter&nbsp;: ${euro(r.trou)} / mois</b><br>
          Après les revenus renseignés${state.epargne > 0 && r.moisEpargne !== Infinity && r.moisEpargne >= 1
            ? `, et hors épargne (elle y pourvoirait environ ${Math.floor(r.moisEpargne)} mois)` : ''}.</p>` : ''}"""
)

# ── 3. Les repères : trois faits décisifs, chacun nommé par ce qu'il est
rem(
    """      <div class="f-faits">
        ${fait(e[C.cap] ? e[C.cap] : '—', e[C.cap] ? 'places dans l’établissement' : 'nombre de places non publié')}
        ${fait(e[C.ash] === 1 ? 'Oui' : e[C.ash] === 2 ? 'À vérifier' : e[C.ash] === 0 ? 'Non' : '—',
               'accepte l’aide sociale du département')}
        ${fait(e[C.statut] != null ? STATUTS[e[C.statut]] : '—', 'qui gère l’établissement')}
        ${fait(e[C.hasN] || '—', e[C.hasN] ? 'note officielle de qualité, de A à D' : 'pas encore évalué')}
      </div>""",
    """      <div class="f-faits">
        ${fait(ashEtat(e), 'Aide sociale')}
        ${fait(e[C.hasN] || 'Non publiée', 'Évaluation publiée')}
        ${fait(e[C.statut] != null ? STATUTS[e[C.statut]] : 'Non renseigné', 'Statut')}
      </div>
      <p class="f-dispo-l">Disponibilités&nbsp;: contactez l’établissement.</p>"""
)

# ── 4. Les actions : une principale, deux secondaires, plus le contact
rem(
    """      <div class="f-cta print-hide">
        ${p ? '<button type="button" class="btn" data-modif>Modifier ma situation</button>'
            : '<button type="button" class="btn" data-modif>Estimer mon reste à charge</button>'}
        <button type="button" class="cta-s mini2" data-cmp="${e[C.fin]}">${libCmp(state.compare.indexOf(e[C.fin]) >= 0)}</button>
        <button type="button" class="cta-s mini2 fav" data-fav="${e[C.fin]}">${state.favoris.indexOf(e[C.fin]) >= 0 ? '♥ Gardé' : '♡ Garder'}</button>
      </div>""",
    """      <div class="f-cta print-hide">
        ${e[C.tel] ? `<a class="btn" href="tel:${esc(String(e[C.tel]).replace(/\\D/g, ''))}" data-tel>Appeler l’établissement</a>` : ''}
        <button type="button" class="cta-s mini2" data-modif>${p ? 'Modifier ma situation' : 'Estimer le budget'}</button>
        <button type="button" class="cta-s mini2" data-cmp="${e[C.fin]}">${libCmp(state.compare.indexOf(e[C.fin]) >= 0)}</button>
        <button type="button" class="cta-s mini2 fav" data-fav="${e[C.fin]}" aria-label="${state.favoris.indexOf(e[C.fin]) >= 0 ? 'Retirer des favoris' : 'Garder pour plus tard'}">${state.favoris.indexOf(e[C.fin]) >= 0 ? '♥ Gardé' : '♡ Garder'}</button>
      </div>"""
)

# ── 5. La localisation : à vol d'oiseau, dit une fois
rem(
    """        <div><h3>${esc(nom(e))}</h3><p class="f-loc">${esc(e[C.ville])} · ${nbfr(+o.dist.toFixed(1))} km de votre point de départ</p></div>""",
    """        <div><h3>${esc(nom(e))}</h3><p class="f-loc">${esc(e[C.ville])} · à ${nbfr(+o.dist.toFixed(1))} km à vol d’oiseau du lieu recherché</p></div>"""
)

# ── 6. Le résumé en une phrase, sans renvoi vers un onglet nommé
rem(
    """    return `Il manque ${euro(manque)} chaque mois : au-delà ${pourMoi() ? 'de vos ressources' : 'des ressources de votre parent'}.
      Les pistes — famille, aide sociale — sont détaillées dans l’onglet « Prix &amp; aides ».`;""",
    """    return `Il manque ${euro(manque)} chaque mois. Voir les financements possibles dans « Prix &amp; aides ».`;"""
)

io.open(P, 'w', encoding='utf-8').write(s)
print('%d blocs posés' % n)
