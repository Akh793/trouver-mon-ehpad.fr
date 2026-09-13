# -*- coding: utf-8 -*-
"""Cas limites : revenus nuls, GIR inconnu, accueil temporaire, type de chambre sans tarif.

Quatre situations dans lesquelles le produit se taisait ou affirmait trop :
  1. une personne sans retraite mais avec d'autres ressources ne déclenchait pas le calcul ;
  2. le GIR « je ne sais pas » produisait un montant d'apparence certaine ;
  3. l'accueil temporaire a ses propres tarifs et ses propres droits : le montant mensuel
     affiché ne le concerne pas, et le filtre laissait croire le contraire ;
  4. un tarif de chambre double manquant était remplacé en silence par la chambre seule
     dans le montant de tête.
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


# ── 1. Des ressources sans retraite restent des ressources
rem(
    "  const perso = () => Number.isFinite(state.revenus) && state.revenus > 0;",
    """  /* Le calcul démarre dès qu'une ressource est connue, d'où qu'elle vienne. Une personne
     sans retraite mais avec un loyer perçu, une rente ou l'allocation de solidarité aux
     personnes âgées n'est pas une personne sans ressources : elle ne doit pas être renvoyée
     à l'affichage des seuls tarifs. */
  const perso = () => (Number.isFinite(state.revenus) ? state.revenus : 0) + (state.autres || 0) > 0;"""
)

# ── 2. Le GIR inconnu reste inconnu, y compris sur le montant affiché
rem(
    "      if (!r.depConnue) second += '<span class=\"tarif t-reserve\">hors aide au quotidien, non déclarée</span>';\n      else if (r.depDouteuse) second += '<span class=\"tarif t-reserve\">tarifs dépendance à confirmer</span>';",
    """      if (!r.depConnue) second += '<span class="tarif t-reserve">hors aide au quotidien, non déclarée</span>';
      else if (r.depDouteuse) second += '<span class="tarif t-reserve">tarifs dépendance à confirmer</span>';
      else if (r.girSuppose) second += '<span class="tarif t-reserve">niveau d’autonomie supposé</span>';
      if (r.chambreSupposee) second += '<span class="tarif t-reserve">tarif de chambre double non déclaré</span>';"""
)
rem(
    "    if (s.chambre === 'cd' && e[C.pcd] == null) notes.push('Cet établissement n’a pas communiqué de prix pour les chambres doubles. Le calcul utilise celui d’une chambre seule — le vrai prix sera sans doute différent.');\n    if (s.gir === '?') notes.push('Le niveau d’autonomie n’est pas connu. Le calcul retient un niveau moyen (GIR 3-4) : le montant réel dépendra de l’évaluation faite par le médecin du département.');",
    """    const chambreSupposee = s.chambre === 'cd' && e[C.pcd] == null;
    if (chambreSupposee) notes.push('Cet établissement n’a pas communiqué de prix pour les chambres doubles. Le calcul utilise celui d’une chambre seule — le vrai prix sera sans doute différent.');
    // Un GIR non connu ne devient pas un GIR moyen : il reste un GIR non connu, et le
    // montant qui en découle porte cette réserve partout où il s'affiche.
    const girSuppose = s.gir === '?';
    if (girSuppose) notes.push('Le niveau d’autonomie n’est pas connu. Le calcul retient un niveau moyen (GIR 3-4) pour donner un ordre de grandeur : le montant réel dépendra de l’évaluation faite par le médecin coordonnateur et le département, et il peut s’en écarter sensiblement.');"""
)
rem(
    "      prixConnu: true, pj, nbRes, reg, pfJour, depConnue, depDouteuse,",
    "      prixConnu: true, pj, nbRes, reg, pfJour, depConnue, depDouteuse, girSuppose, chambreSupposee,"
)

# ── 3. L'accueil temporaire : un autre tarif, d'autres droits
rem(
    "      if (e[C.temp] != null) chips.push(`<span class=\"chip\">Accueil temporaire : ${euro2(e[C.temp])}/jour</span>`);",
    "      if (e[C.temp] != null) chips.push(`<span class=\"chip\">Accueil temporaire : ${euro2(e[C.temp])}/jour</span>`);"
)
rem(
    """    if (s.tempOnly) sorties.push('<button type="button" class="mini2" data-sortie="temp">Ne plus exiger l’accueil temporaire</button>');""",
    """    if (s.tempOnly) sorties.push('<button type="button" class="mini2" data-sortie="temp">Ne plus exiger l’accueil temporaire</button>');"""
)
rem(
    """        ${o.prix ? '<h4>L’évolution du tarif</h4>' + blocPrix(o.prix) : ''}""",
    """        ${e[C.temp] != null ? `<h4 class="f-t1">Si le séjour est temporaire</h4>
          <div class="ln"><span>Tarif d’hébergement temporaire déclaré</span><b>${euro2(e[C.temp])}/jour</b></div>
          <p class="f-note">Les montants calculés sur cette page portent tous sur un
          <b>hébergement permanent</b>. L’hébergement temporaire est un autre régime&nbsp;: son tarif
          est distinct, l’APA y obéit à d’autres règles, l’aide sociale à l’hébergement n’y est pas
          acquise, et il est exclu de l’expérimentation de fusion des financements. Nous ne le
          calculons pas&nbsp;: demandez à l’établissement le coût d’un séjour temporaire, et au
          département les aides mobilisables pour cette formule.</p>` : ''}
        ${o.prix ? '<h4>L’évolution du tarif</h4>' + blocPrix(o.prix) : ''}"""
)

io.open(P, 'w', encoding='utf-8').write(s)
print('%d blocs corrigés' % n)
