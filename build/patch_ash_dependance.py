# -*- coding: utf-8 -*-
"""Le scénario d'aide sociale ne portait que sur l'hébergement, sans le dire.

L'aide sociale à l'hébergement ne couvre pas la part « aide au quotidien » : le résident
la règle en plus. Le total affiché sous aide sociale était donc systématiquement inférieur
à ce qui sera réellement payé, sans qu'aucune ligne ne le signale.
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


rem(
    """      ash = { partParent, gardeMini, garde, reserveConjoint, prixAsh, prixRetenu,
        prixEstime: prixAsh == null, reste, aConfirmer: e[C.ash] === 2 };""",
    """      // L'aide sociale porte sur l'hébergement seul. La part « aide au quotidien »
      // (participation forfaitaire, ou tarif dépendance net d'APA) reste à la charge du
      // résident : elle doit apparaître, sinon le scénario sous-estime la dépense réelle.
      const depReste = depConnue ? Math.max(0, dependance - apa) : null;
      ash = { partParent, gardeMini, garde, reserveConjoint, prixAsh, prixRetenu,
        prixEstime: prixAsh == null, reste, aConfirmer: e[C.ash] === 2,
        depReste, depConnue, reg,
        // ce que la personne sortira réellement chaque mois dans ce scénario
        sortie: partParent + (depReste || 0) };"""
)

rem(
    """            <div class="ln"><span>Il lui reste, pour ses dépenses personnelles</span><b>${euro(r.ash.garde)}/mois</b></div>""",
    """            ${r.ash.depConnue && r.ash.depReste > 0
              ? `<div class="ln"><span>Et, en plus, l’aide aux gestes du quotidien</span><b>− ${euro(r.ash.depReste)}/mois</b></div>
                 <p class="f-note">L’aide sociale ne couvre que l’hébergement. ${r.ash.reg === 'exp'
                   ? 'La participation forfaitaire reste due.'
                   : 'Le tarif dépendance restant après APA reste dû.'}
                 Au total, votre parent sortirait <b>${euro(r.ash.sortie)}</b> par mois dans ce scénario.</p>`
              : r.ash.depConnue
                ? ''
                : `<p class="f-note">La part «&nbsp;aide au quotidien&nbsp;» n’a pas pu être chiffrée&nbsp;:
                   elle s’ajoutera à ce montant, car l’aide sociale ne couvre que l’hébergement.</p>`}
            <div class="ln"><span>Il lui reste, pour ses dépenses personnelles</span><b>${euro(r.ash.garde)}/mois</b></div>"""
)

io.open(P, 'w', encoding='utf-8').write(s)
print('%d blocs corrigés' % n)
