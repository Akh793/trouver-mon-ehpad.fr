# -*- coding: utf-8 -*-
"""Réécriture du cœur de calcul de site/app.js.

Trois changements de fond :
  1. le régime de financement de la dépendance devient explicite (colonne « reg ») ;
  2. la facture, la trésorerie et l'avantage fiscal deviennent trois résultats distincts ;
  3. les extrapolations sur les places disparaissent.

Le script est idempotent : il vérifie la présence de chaque bloc avant de le remplacer.
"""
import io, os, sys, re

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site', 'app.js')
s = io.open(P, encoding='utf-8').read()
n = 0


def rem(avant, apres, obligatoire=True):
    global s, n
    if avant not in s:
        if obligatoire:
            print('INTROUVABLE :', avant[:90].replace('\n', ' '))
            sys.exit(1)
        return False
    s = s.replace(avant, apres, 1)
    n += 1
    return True


# ─────────────────────────────────────────────────────────────────────────────
# 1. La colonne « reg » et le barème de la participation forfaitaire
# ─────────────────────────────────────────────────────────────────────────────
rem(
    "dens:43, occ:44 };",
    "dens:43, occ:44, reg:45 };"
)

rem(
    "  const COULEUR = {",
    """  /* ---------- Régime de financement de la dépendance ----------
     Dans 23 territoires, l'expérimentation de fusion des financements soins et dépendance
     a remplacé, depuis le 1er juillet 2025, le tarif dépendance par GIR et l'APA en
     établissement par une participation journalière forfaitaire, identique pour tous.
     Le régime vient du territoire d'implantation, jamais des tarifs déclarés :
     REGIMES.note explique pourquoi. */
  const REGIMES = {
    exp: {
      lib: 'Expérimentation de fusion des financements soins et dépendance',
      court: 'participation forfaitaire',
      depuis: '2025-07-01',
      // Montants nationaux, uniformes, par jour. Le dernier applicable fait foi.
      pf: [
        { debut: '2025-07-01', montant: 6.10, src: 'Arrêté du 6 juin 2025 (NOR TSSA2516495A)' },
        { debut: '2026-01-01', montant: 6.16, src: 'Instruction DGCS du 16 juin 2026, annexe 4' },
      ],
      note: 'Le résident ne paie plus un tarif lié à son GIR, ni une participation qui augmente avec ses ressources : une somme forfaitaire par jour, la même pour tous.',
    },
    classique: {
      lib: 'Régime de droit commun',
      court: 'tarif dépendance et APA',
      note: 'Le résident paie au minimum le tarif dépendance GIR 5-6. Au-delà, sa participation augmente avec ses ressources, selon un barème national.',
    },
  };
  /** Participation forfaitaire applicable à une date donnée. */
  function participationForfaitaire(iso) {
    const d = iso || new Date().toISOString().slice(0, 10);
    let r = null;
    REGIMES.exp.pf.forEach((p) => { if (p.debut <= d) r = p; });
    return r;
  }
  const regimeDe = (e) => (e[C.reg] === 'exp' ? 'exp' : e[C.reg] === 'classique' ? 'classique' : 'inconnu');

  const COULEUR = {"""
)

# ─────────────────────────────────────────────────────────────────────────────
# 2. Le cœur du calcul
# ─────────────────────────────────────────────────────────────────────────────
ancien = """    const heberg = pj * mois * nbRes;
    const tg = tarifGir(e, s.gir), t56 = e[C.t56];
    let dependance = 0, apa = 0, apaConnue = false;
    if (tg != null && t56 != null) {
      dependance = tg * mois * nbRes;
      const r = apaEtablissement(tg * mois, t56 * mois, ressourcesTotales(s), s.couple || s.deuxResidents);
      apa = r.apa * nbRes; apaConnue = true;
      if (Math.abs(tg - t56) < 0.01) notes.push('Cet établissement facture la même somme quel que soit le niveau d’autonomie. Dans ce cas, l’aide du département (l’APA) tombe mécaniquement à zéro dans notre calcul. Appelez-le : le tarif réellement appliqué est probablement différent.');
    } else {
      notes.push('Cet établissement n’a pas communiqué le prix de l’aide au quotidien. Seul le logement est calculé ici : la facture réelle sera plus élevée.');
    }

    const apl = Math.max(0, s.aideLogement || 0);
    const baseIR = Math.max(0, heberg + dependance - apa - apl);
    const plafondMois = (BAREME.irPlafond * nbRes) / 12;
    const ir = s.imposable ? BAREME.irTaux * Math.min(baseIR, plafondMois) : 0;

    const rac = Math.max(0, heberg + dependance - apa - apl - ir);
    const R = ressourcesTotales(s);"""

nouveau = """    const heberg = pj * mois * nbRes;
    const reg = regimeDe(e);

    // ── la part « aide au quotidien » de la facture, selon le régime du territoire
    let dependance = 0, apa = 0, apaConnue = false, pfJour = null, depConnue = false;
    if (reg === 'exp') {
      // Participation forfaitaire nationale : ni GIR, ni condition de ressources.
      // On retient le montant en vigueur, pas celui déclaré à la CNSA, souvent antérieur.
      const pf = participationForfaitaire();
      pfJour = pf.montant;
      dependance = pf.montant * mois * nbRes;
      depConnue = true;
      apaConnue = false;           // l'APA en établissement est supprimée dans ces territoires
      const declare = e[C.t56];
      if (declare != null && Math.abs(declare - pf.montant) > 0.01) {
        notes.push('Cet établissement a déclaré ' + euro2(declare) + ' par jour lors de la dernière publication. '
          + 'Le calcul retient le montant national en vigueur, ' + euro2(pf.montant) + ' — ' + pf.src + '.');
      }
    } else if (reg === 'inconnu') {
      notes.push('Le régime de financement applicable à cet établissement n’a pas pu être établi. '
        + 'La part « aide au quotidien » n’est donc pas calculée : demandez-la à l’établissement.');
    } else {
      const tg = tarifGir(e, s.gir), t56 = e[C.t56];
      if (tg != null && t56 != null) {
        dependance = tg * mois * nbRes;
        depConnue = true;
        const r = apaEtablissement(tg * mois, t56 * mois, ressourcesTotales(s), s.couple || s.deuxResidents);
        apa = r.apa * nbRes; apaConnue = true;
        if (Math.abs(tg - t56) < 0.01) {
          notes.push('Cet établissement déclare le même tarif quel que soit le niveau d’autonomie, '
            + 'alors qu’il relève du régime de droit commun. L’aide du département ressort donc à zéro ici. '
            + 'Demandez-lui le tarif qui s’appliquera réellement.');
        }
      } else {
        notes.push('Cet établissement n’a pas communiqué le prix de l’aide au quotidien. '
          + 'Seul le logement est calculé ici : la facture réelle sera plus élevée.');
      }
    }

    // ── 1. LA FACTURE : ce que l'établissement réclame chaque mois
    const facture = heberg + dependance;

    // ── 2. LES AIDES, distinguées par leur modalité de versement
    //    apa : versée directement à l'établissement, elle diminue la facture
    //    apl : versée au résident ou à l'établissement selon les cas, mais mensuelle
    const aplSaisi = Math.max(0, s.aideLogement || 0);
    const aplConfirme = s.aplEtab && state.selection && s.aplEtab === e[C.fin];
    // Une aide notifiée pour un établissement ne vaut pas pour les autres.
    const apl = s.aplPortee === 'partout' ? aplSaisi : (aplConfirme ? aplSaisi : 0);
    const aplHypothese = aplSaisi > 0 && !aplConfirme && s.aplPortee === 'partout';

    // ── 3. CE QU'IL FAUT DÉCAISSER CHAQUE MOIS, avant tout effet fiscal
    const decaisse = Math.max(0, facture - apa - apl);

    // ── 4. L'AVANTAGE FISCAL : annuel, différé, et seulement potentiel
    const R = ressourcesTotales(s);
    const fisc = avantageFiscal(facture - apa - apl, s, nbRes);
    const ir = 0;                 // ne diminue plus le mensuel : il est sorti du décaissement
    const rac = decaisse;         // « reste à charge » = ce qu'il faut sortir chaque mois"""

rem(ancien, nouveau)

# ─────────────────────────────────────────────────────────────────────────────
# 3. Trésorerie : l'épargne se calcule sur le décaissement réel
# ─────────────────────────────────────────────────────────────────────────────
rem(
    """    const dispo = Math.max(0, R - gardeMini - reserveConjoint);
    const trou = Math.max(0, rac - dispo);
    const moisEpargne = trou > 0 && s.epargne > 0 ? s.epargne / trou : (trou > 0 ? 0 : Infinity);

    let couleur = 'vert';
    if (trou > 0) couleur = moisEpargne >= 60 ? 'orange' : 'rouge';""",
    """    // Ce que la personne peut réellement consacrer chaque mois au décaissement.
    const dispo = Math.max(0, R - gardeMini - reserveConjoint);
    const trou = Math.max(0, decaisse - dispo);
    // L'épargne est consommée par le flux de trésorerie, pas par un montant après impôt.
    const moisEpargne = trou > 0 && s.epargne > 0 ? s.epargne / trou : (trou > 0 ? 0 : Infinity);

    let couleur = 'vert';
    if (trou > 0) couleur = moisEpargne >= 60 ? 'orange' : 'rouge';"""
)

# ─────────────────────────────────────────────────────────────────────────────
# 4. Les places : on retire l'extrapolation, on garde le fait sectoriel daté
# ─────────────────────────────────────────────────────────────────────────────
rem(
    """    // disponibilité estimée (moyenne de segment, jamais un relevé)
    let dispoEst = null;
    if (e[C.occ] != null) {
      const rot = ROTATION[e[C.statut]] != null ? ROTATION[e[C.statut]] : ROTATION.FR;
      const cap = e[C.cap] || null;
      dispoEst = { occ: e[C.occ], libres100: +(100 - e[C.occ]).toFixed(1), cap,
        vac: cap ? +(cap * (1 - e[C.occ] / 100)).toFixed(1) : null,
        jours: cap ? Math.round(365 / (cap * rot)) : null, rot: Math.round(rot * 1000) / 10 };
    }""",
    """    // Aucune extrapolation de places libres : le taux d'occupation est une moyenne de
    // segment issue d'une enquête, il ne dit rien de cet établissement un jour donné.
    // On conserve le fait sectoriel, daté et nommé comme tel.
    const secteur = e[C.occ] != null ? { occ: e[C.occ] } : null;"""
)

# ─────────────────────────────────────────────────────────────────────────────
# 5. L'objet de résultat
# ─────────────────────────────────────────────────────────────────────────────
rem(
    """    return { prixConnu: true, pj, nbRes, heberg, dependance, apa, apaConnue, apl, ir, rac,
      total: heberg + dependance, aides: heberg + dependance - rac,
      trou, moisEpargne, couleur, ash, famille, dispoEst, vieux, notes };""",
    """    return {
      prixConnu: true, pj, nbRes, reg, pfJour, depConnue,
      heberg, dependance,
      facture,                       // 1. ce que l'établissement facture
      apa, apaConnue, apl, aplHypothese,
      decaisse,                      // 2. ce qu'il faut sortir chaque mois
      fisc,                          // 3. avantage fiscal annuel, potentiel et différé
      rac, total: facture, aides: apa + apl,
      trou,                          // 5. contribution complémentaire nécessaire
      moisEpargne, couleur, ash, famille, secteur, vieux, notes,
    };"""
)

io.open(P, 'w', encoding='utf-8').write(s)
print('%d blocs remplacés dans app.js' % n)
