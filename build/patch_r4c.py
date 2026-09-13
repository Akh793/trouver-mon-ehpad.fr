# -*- coding: utf-8 -*-
"""Refonte rédactionnelle — lot 4c : l'onglet Essentiel cesse de répéter l'en-tête.

Un défaut de fond découvert en vérifiant le rendu : le complément à financer était
calculé de deux façons différentes et affiché deux fois, avec deux valeurs.
L'en-tête donnait `r.trou`, qui préserve un minimum de reste à vivre ; l'onglet
recalculait « reste à charge − revenus », sans ce minimum. Sur le même écran :
844 € d'un côté, 684 € de l'autre. Une seule définition subsiste, celle du moteur.

L'onglet perdait aussi sa raison d'être en répétant la distance, le prix et la
mention de disponibilité déjà présents au-dessus.
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


# ── 1. Une seule définition du complément à financer
rem(
    """  function resumeSimple(o) {
    const r = o.r, dispo = state.revenus + (state.autres || 0);
    if (r.rac <= dispo) {
      return `${mot('resMaj')} (${euro(dispo)}/mois) couvrent cette somme.`;
    }
    const manque = r.rac - dispo;
    if (state.epargne > 0 && r.moisEpargne !== Infinity && r.moisEpargne >= 12) {
      return `Il manque ${euro(manque)} chaque mois. L’épargne déclarée y pourvoirait environ
        ${Math.floor(r.moisEpargne)} mois.`;
    }
    return `Il manque ${euro(manque)} chaque mois. Voir les financements possibles dans « Prix &amp; aides ».`;
  }""",
    """  /** Une phrase sur ce que le budget veut dire pour cette situation.
      Le complément vient de `r.trou`, la seule définition du moteur : il préserve
      un minimum de reste à vivre, ce qu'une simple soustraction « budget − revenus »
      ignorait — d'où deux chiffres différents affichés sur le même écran. */
  function resumeSimple(o) {
    const r = o.r;
    if (r.trou <= 0) return `Les ressources renseignées couvrent ce budget.`;
    if (state.epargne > 0 && r.moisEpargne !== Infinity && r.moisEpargne >= 12) {
      return `L’épargne renseignée couvrirait ce complément environ ${Math.floor(r.moisEpargne)} mois.`;
    }
    return `Voir les financements possibles dans « Prix &amp; aides ».`;
  }"""
)

# ── 2. L'onglet ne redit pas ce que l'en-tête a déjà dit
rem(
    """    l.push(`<div class="ln"><span>À quelle distance de votre point de départ</span><b>${nbfr(+o.dist.toFixed(1))} km</b></div>`);
    if (r.prixConnu) l.push(`<div class="ln"><span>Prix du logement, par jour</span><b>${euro2(r.pj)}</b></div>`);
    if (r.apaConnue && r.apa > 0) l.push(`<div class="ln"><span>Aide du département versée à l’établissement</span><b>${euro(r.apa)}/mois</b></div>`);
    if (o.prix) l.push(`<div class="ln"><span>De combien le prix a augmenté depuis ${o.prix.d}</span><b class="${o.prix.e < 0 ? 'vert' : 'rouge'}">${pct(o.prix.e)}</b></div>`);
    l.push(`<div class="ln"><span>Aide au quotidien</span><b>${r.reg === 'exp'
      ? 'forfait de ' + euro2(r.pfJour) + '/jour'
      : r.reg === 'inconnu' ? 'régime à confirmer' : 'selon le niveau d’autonomie'}</b></div>`);
    l.push('<p class="f-note">Disponibilité&nbsp;: aucune source publique ne donne les places libres d’un établissement. '
      + 'À demander directement.</p>');
    if (r.moisEpargne !== Infinity && r.trou > 0 && state.epargne > 0)
      l.push(`<div class="ln"><span>Combien de temps l’épargne tiendrait</span><b>${Math.floor(r.moisEpargne)} mois</b></div>`);
    const tete = r.prixConnu && perso()
      ? `<p class="f-resume">${resumeSimple(o)}</p>` : '';
    return tete + l.join('') +
      r.notes.map((n) => `<p class="warn">${esc(n)}</p>`).join('') +
      (r.ash && r.ash.aConfirmer ? '<p class="warn">L’habilitation à l’aide sociale est à vérifier auprès de l’établissement.</p>' : '') +
      '<p class="f-src">Prix : Caisse nationale de solidarité pour l’autonomie. Identité et habilitation : répertoire FINESS. Évaluation : Haute Autorité de santé. Le détail est dans les autres onglets.</p>';""",
    """    if (r.prixConnu) l.push(`<div class="ln"><span>Hébergement</span><b>${euro2(r.pj)}/jour</b>${e[C.maj] ? `<i class="ln-d">tarif ${mfr(e[C.maj])}</i>` : ''}</div>`);
    l.push(`<div class="ln"><span>Aide au quotidien</span><b>${r.reg === 'exp'
      ? euro2(r.pfJour) + '/jour, forfait'
      : r.reg === 'inconnu' ? 'régime à confirmer' : 'selon le GIR'}</b></div>`);
    if (r.apaConnue && r.apa > 0) l.push(`<div class="ln"><span>APA versée à l’établissement</span><b>− ${euro(r.apa)}/mois</b></div>`);
    if (o.prix) l.push(`<div class="ln"><span>Évolution du tarif ${o.prix.d}–${o.prix.f}</span><b class="${o.prix.e < 0 ? 'vert' : 'rouge'}">${pct(o.prix.e)}</b></div>`);
    if (e[C.cap]) l.push(`<div class="ln"><span>Capacité</span><b>${nbfr(e[C.cap])} places</b><i class="ln-d">ne dit rien des places libres</i></div>`);
    const tete = r.prixConnu && perso()
      ? `<p class="f-resume">${resumeSimple(o)}</p>` : '';
    return tete + l.join('') +
      r.notes.map((n) => `<p class="warn">${esc(n)}</p>`).join('') +
      '<p class="f-src"><a href="notre-methodologie.html">Sources et dates</a> — tarifs CNSA, identité FINESS, évaluation HAS.</p>';"""
)

io.open(P, 'w', encoding='utf-8').write(s)
print('%d blocs posés' % n)
