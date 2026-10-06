# -*- coding: utf-8 -*-
"""Bloc de réassurance (06/10/2026) : avis Trustpilot, réutilisation data.gouv.fr, engagements.
Un seul texte, inséré dans les trois pieds de page (accueil, pages de contenu, pages annexes)
et sous la liste des résultats du calculateur. Icônes génériques en SVG : ni le logo de
Trustpilot (marque déposée) ni la Marianne (réservée aux services de l'État)."""

TRUSTPILOT = 'https://fr.trustpilot.com/review/trouver-mon-ehpad.fr'
# Adresse vérifiée par l'API data.gouv.fr le 06/10/2026 (l'adresse /reuses/trouver-mon-ehpad-fr/ renvoie 404)
DATAGOUV = 'https://www.data.gouv.fr/reuses/trouver-mon-ehpad-calculateur-du-reste-a-charge-net-aides-apa-apl-2026'

ETOILE = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2.6l2.8 6 6.5.6-4.9 4.3 1.5 6.4L12 16.6l-5.9 3.3 1.5-6.4-4.9-4.3 6.5-.6z"/></svg>')
DONNEES = ('<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round">'
           '<ellipse cx="12" cy="5.5" rx="7.5" ry="2.8"/><path d="M4.5 5.5v6.5c0 1.5 3.4 2.8 7.5 2.8s7.5-1.3 7.5-2.8V5.5"/>'
           '<path d="M4.5 12v6.5c0 1.5 3.4 2.8 7.5 2.8s7.5-1.3 7.5-2.8V12"/></svg>')


def bloc(variante=''):
    """variante : '' (pied de page) ou 'reassur-res' (sous les résultats)."""
    return (f'<div class="reassur {variante}" role="group" aria-label="Avis et engagements">'
            f'<a class="re-badge re-tp" href="{TRUSTPILOT}" target="_blank" rel="noopener noreferrer">'
            f'<span class="re-ico">{ETOILE}</span><span class="re-txt"><b>Avis sur Trustpilot</b>'
            f'<small>Lisez ou laissez un avis</small></span></a>'
            f'<a class="re-badge re-dg" href="{DATAGOUV}" target="_blank" rel="noopener noreferrer">'
            f'<span class="re-ico">{DONNEES}</span><span class="re-txt"><b>Réutilisation référencée</b>'
            f'<small>sur data.gouv.fr</small></span></a>'
            f'<div class="re-eng"><span>100&nbsp;% gratuit</span><span>Sans inscription</span><span>0 démarchage</span></div>'
            f'</div>')


# Styles : build/site.css, section « Bloc de réassurance ».
