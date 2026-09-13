# -*- coding: utf-8 -*-
"""Les montants annuels ne se déduisent plus d'un mois moyen multiplié par douze.

30,5 × 12 = 366 : toute somme annuelle obtenue en multipliant le mensuel par douze
comptait un jour de trop, et deux les années non bissextiles. Les montants annuels
sont désormais calculés depuis les tarifs journaliers et le nombre réel de jours.
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


# ── 1. Le nombre de jours d'une année, et l'avertissement de convention
rem(
    "  const M = () => META.month;",
    """  const M = () => META.month;
  /** Nombre de jours de l'année en cours : 366 une année bissextile, 365 sinon.
      Multiplier un montant mensuel par douze reviendrait à compter 30,5 × 12 = 366 jours
      chaque année : un jour de trop sur trois années sur quatre. */
  function joursAnnee(annee) {
    const y = annee || new Date().getFullYear();
    return (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0 ? 366 : 365;
  }"""
)

# ── 2. L'avantage fiscal : assiette journalière, prorata en jours
rem(
    """  function avantageFiscal(fraisMensuels, s, nbRes) {
    const mois = Math.max(0, Math.min(12, s.moisAnnee == null ? 12 : s.moisAnnee));
    const plafondDepenses = BAREME.irPlafond * nbRes * (mois / 12);
    const plafondReduction = plafondDepenses * BAREME.irTaux;
    const depenses = Math.max(0, fraisMensuels) * mois;""",
    """  function avantageFiscal(fraisJour, s, nbRes) {
    const mois = Math.max(0, Math.min(12, s.moisAnnee == null ? 12 : s.moisAnnee));
    // Le plafond de 10 000 € est annuel et ne se proratise pas en jours mais en
    // durée de séjour : on retient les mois déclarés, faute de dates précises.
    const plafondDepenses = BAREME.irPlafond * nbRes * (mois / 12);
    const plafondReduction = plafondDepenses * BAREME.irTaux;
    // L'assiette, elle, se compte en jours réels : pas de mois moyen multiplié par douze.
    const jours = Math.round(joursAnnee() * (mois / 12));
    const depenses = Math.max(0, fraisJour) * jours;"""
)
rem(
    """      moisRetenus: mois,
      depenses,                         // frais engagés sur la période""",
    """      moisRetenus: mois,
      joursRetenus: jours,
      depenses,                         // frais engagés sur la période, en jours réels"""
)

# ── 3. L'appel : on passe un montant journalier, pas un mensuel
rem(
    "    const fisc = avantageFiscal(facture - apa - apl, s, nbRes);",
    """    // Assiette journalière : (facture − aides) ramenée au jour, pour éviter
    // l'arrondi du mois moyen dans un montant annuel.
    const fisc = avantageFiscal((facture - apa - apl) / mois, s, nbRes);"""
)

# ── 4. Le cumul annuel du scénario d'aide sociale
rem(
    """              ? `<p class="f-note">Ce montant s’accumule tant que dure le séjour, à raison de
                 <b>${euro(r.ash.reste * 12)} par an</b> au rythme actuel.""",
    """              ? `<p class="f-note">Ce montant s’accumule tant que dure le séjour, à raison de
                 <b>${euro((r.ash.reste / M()) * joursAnnee())} par an</b> au rythme actuel.""",
)

io.open(P, 'w', encoding='utf-8').write(s)
print('%d blocs corrigés' % n)
