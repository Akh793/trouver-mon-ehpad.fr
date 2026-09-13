# -*- coding: utf-8 -*-
"""Exports CSV : injection de formule, en-têtes désalignés, reproductibilité.

Trois défauts :
  1. une cellule commençant par =, +, -, @, tabulation ou retour chariot est exécutée
     comme une formule à l'ouverture dans un tableur — un nom d'établissement suffit ;
  2. deux colonnes d'en-tête ne correspondaient plus aux données servies après le
     retrait des extrapolations de places ;
  3. un export ne portait ni sa date, ni la version des données, ni les paramètres
     de la recherche : impossible de le reproduire ou de le dater plus tard.
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


# ── 1. Une seule fabrique de CSV, qui neutralise les formules
rem(
    """  function telecharge(lignes, nomFichier) {
    const csv = lignes.map((l) => l.map((v) => `"${String(v).replace(/"/g, '""')}"`).join(';')).join('\\r\\n');
    const url = URL.createObjectURL(new Blob(['\\ufeff' + csv], { type: 'text/csv;charset=utf-8' }));""",
    """  /** Neutralise l'injection de formule : un tableur exécute toute cellule commençant
      par =, +, - ou @, ainsi que par une tabulation ou un retour chariot. Le préfixe
      apostrophe force l'interprétation en texte, sans changer ce que l'utilisateur lit. */
  function celluleCsv(v) {
    let t = v === null || v === undefined ? '' : String(v);
    if (/^[=+\\-@\\t\\r]/.test(t)) t = "'" + t;
    return '"' + t.replace(/"/g, '""') + '"';
  }
  /** En-tête de provenance : un export daté, versionné et rejouable. */
  function enteteExport() {
    const s = state;
    return [
      ['# trouver-mon-ehpad.fr — export du ' + new Date().toLocaleString('fr-FR')],
      ['# Données : version ' + META.version + ', barèmes vérifiés le ' + dfr(META.lastVerified)
        + (window.COUVERTURE ? ', couverture mesurée le ' + dfr(window.COUVERTURE.date) : '')],
      ['# Recherche : ' + (s.commune ? s.commune.nom + ' (' + s.commune.cp + ')' : s.cp || 'non précisée')
        + ', rayon ' + s.rayon + ' km, tri « ' + s.tri + ' »'],
      ['# Montants calculés avec un mois moyen de ' + String(M()).replace('.', ',') + ' jours. '
        + 'Ils dépendent de la situation saisie et ne valent pas devis.'],
      [''],
    ];
  }
  function telecharge(lignes, nomFichier) {
    const csv = enteteExport().concat(lignes)
      .map((l) => l.map(celluleCsv).join(';')).join('\\r\\n');
    const url = URL.createObjectURL(new Blob(['\\ufeff' + csv], { type: 'text/csv;charset=utf-8' }));"""
)

# ── 2. L'export de la liste passe par la même fabrique, avec des en-têtes justes
rem(
    """      'criteres_imperatifs_18', 'hygiene', 'reste_a_charge_mois', 'apa_mois', 'occupation_segment_%', 'jours_entre_liberations'];""",
    """      'criteres_imperatifs_18', 'hygiene', 'a_decaisser_mois', 'apa_mois', 'occupation_moyenne_du_segment_%',
      'regime_dependance'];"""
)
rem(
    """    const csv = [head, ...lignes].map((l) => l.map((v) => `"${String(v).replace(/"/g, '""')}"`).join(';')).join('\\r\\n');
    const url = URL.createObjectURL(new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' }));
    const a = document.createElement('a');
    a.href = url; a.download = `ehpad-${state.commune ? state.commune.cp : 'selection'}-${state.rayon}km.csv`;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }""",
    """    telecharge([head, ...lignes], `ehpad-${state.commune ? state.commune.cp : 'selection'}-${state.rayon}km.csv`);
  }"""
)
rem(
    "      o.r.prixConnu ? Math.round(o.r.rac) : '', o.r.apaConnue ? Math.round(o.r.apa) : '',",
    "      o.r.prixConnu ? Math.round(o.r.decaisse) : '', o.r.apaConnue ? Math.round(o.r.apa) : '',"
)

io.open(P, 'w', encoding='utf-8').write(s)
print('%d blocs corrigés' % n)
