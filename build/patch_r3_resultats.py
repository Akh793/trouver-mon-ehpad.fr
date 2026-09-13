# -*- coding: utf-8 -*-
"""Refonte rédactionnelle — lot 3 : les résultats.

La médiane s'affichait en très gros caractères au-dessus de la liste, au même
format que le montant d'un établissement : rien ne disait qu'elle ne correspondait
à aucune maison en particulier. Elle devient un repère, à côté du nombre
d'établissements, et perd la place du chiffre dominant.

Le montant est désormais nommé selon ce qu'il est : tarif avant aides quand la
situation n'est pas renseignée, budget estimé quand elle l'est, calcul incomplet
quand une donnée manque. « Aucune aide » ne se dit plus quand l'aide est
simplement inconnue.
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


patch(os.path.join('..', 'site', 'app.js'), [
    ("""    $('res-titre').textContent = `${list.length} EHPAD à ${s.rayon} km ${de(s.commune.nom)}`;
    $('res-chiffre').textContent = med != null ? euro(med) : '—';
    $('res-sous').innerHTML = med == null
      ? 'aucun établissement de cette sélection n’a déclaré son tarif'
      : p
        ? `reste à charge médian pour ${mot('titre')} · de <b>${euro(mini)}</b> à <b>${euro(maxi)}</b> par mois${rouges ? ` · <b>${rouges}</b> hors de portée sans aide sociale ni aide de la famille` : ''}`
        : `tarif médian, avant les aides · de <b>${euro(mini)}</b> à <b>${euro(maxi)}</b> par mois · <b>indiquez ${mot('retraite')}</b> pour voir ce qui resterait à payer`;""",
     """    // Le nombre d'établissements devient le chiffre de tête : c'est lui le résultat
    // de la recherche. La médiane le suit comme repère, jamais comme un prix.
    $('res-titre').textContent = 'Les EHPAD dans cette zone';
    $('res-chiffre').textContent = `${list.length} établissement${list.length > 1 ? 's' : ''}`;
    const sansTarif = list.length - avecPrix.length;
    if (med == null) {
      $('res-sous').innerHTML = `à ${s.rayon} km ${esc(de(s.commune.nom))} · aucun n’a déclaré son tarif`;
    } else {
      // Le mot dit ce que le chiffre mesure : un tarif affiché, ou un budget calculé.
      const lib = p ? 'Budget médian estimé' : 'Prix médian de la sélection';
      $('res-sous').innerHTML = `à ${s.rayon} km ${esc(de(s.commune.nom))}`
        + ` · <b>${lib}&nbsp;: ${euro(med)}</b>/mois, de ${euro(mini)} à ${euro(maxi)}`
        + ` sur ${avecPrix.length} établissement${avecPrix.length > 1 ? 's' : ''} comparable${avecPrix.length > 1 ? 's' : ''}`
        + (sansTarif ? ` · ${sansTarif} sans tarif déclaré` : '')
        + (p && rouges ? ` · <b>${rouges}</b> au-delà des ressources renseignées` : '')
        + (p ? '' : ` · <b>indiquez ${mot('retraite')}</b> pour estimer le budget`);
    }"""),

    # ── La carte de résultat nomme son montant
    ("""    if (!r.prixConnu) { montant = 'Tarif non déclaré'; lib = ''; }
    else if (p) {
      montant = euro(r.rac); lib = 'à financer / mois';
      second = r.aides >= 1
        ? `<span class="tarif">Tarif&nbsp;: ${euro(r.total)} · aides −${euro(r.aides)}</span>`
        : `<span class="tarif">Tarif&nbsp;: ${euro(r.total)} · aucune aide déduite</span>`;""",
     """    if (!r.prixConnu) { montant = 'Tarif non renseigné'; lib = ''; }
    else if (p) {
      montant = euro(r.decaisse); lib = r.depConnue ? 'budget estimé / mois' : 'calcul incomplet / mois';
      // « Aucune aide » n'est vrai que si le calcul a pu en chercher une. Quand le
      // régime supprime l'APA, ou quand la part dépendance manque, ce n'est pas
      // l'absence d'aide qu'on observe, c'est l'absence d'information.
      second = r.aides >= 1
        ? `<span class="tarif">Facture&nbsp;: ${euro(r.facture)} · aides −${euro(r.aides)}</span>`
        : r.reg === 'exp'
          ? `<span class="tarif">Facture&nbsp;: ${euro(r.facture)} · forfait inclus</span>`
          : `<span class="tarif">Facture&nbsp;: ${euro(r.facture)}</span>`;"""),

    ("""      montant = euro(r.total); lib = 'tarif / mois';
      second = '<span class="tarif">avant les aides</span>';""",
     """      montant = euro(r.facture); lib = 'tarif / mois';
      second = '<span class="tarif">avant les aides</span>';"""),

    # ── Le tri n'est pas une recommandation
    ("""    $('barre-n').textContent = list.length
      ? `${list.length} établissement${list.length > 1 ? 's' : ''}${list.length > state.nbAffiches ? ` · ${Math.min(state.nbAffiches, list.length)} affichés` : ''}`
      : 'aucun résultat';""",
     """    $('barre-n').textContent = list.length
      ? `${list.length} établissement${list.length > 1 ? 's' : ''}${list.length > state.nbAffiches ? ` · ${Math.min(state.nbAffiches, list.length)} affichés` : ''}`
      : 'Aucun établissement ne correspond à ces critères.';"""),
])

print('%d blocs posés' % n)
