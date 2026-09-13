# -*- coding: utf-8 -*-
"""Avantage fiscal : annuel, plafonné, proratisé, et jamais retranché du mensuel."""
import io, os, sys

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site', 'app.js')
s = io.open(P, encoding='utf-8').read()
n = 0


def rem(a, b):
    global s, n
    if a not in s:
        print('INTROUVABLE :', a[:100].replace('\n', ' '))
        sys.exit(1)
    s = s.replace(a, b, 1)
    n += 1


# ── la fonction, posée juste avant calcule()
rem(
    "  function calcule(e, s) {",
    """  /** Avantage fiscal annuel POTENTIEL de la personne hébergée.

      Ce n'est pas une aide : c'est une réduction d'impôt, versée l'année suivante, et
      seulement si la personne paie effectivement de l'impôt. Elle ne doit donc jamais
      diminuer la somme à sortir chaque mois.

      Ce que le calcul applique :
        — assiette : frais d'hébergement et de dépendance restant à charge, APA et aide
          au logement déjà déduites ;
        — plafond de dépenses : 10 000 € par an et PAR PERSONNE hébergée ;
        — taux : 25 %, donc 2 500 € de réduction au maximum et par personne ;
        — prorata : seuls les mois réellement passés en établissement comptent.

      Ce que le calcul NE PEUT PAS savoir, et qu'il annonce :
        — le montant d'impôt réellement dû. Une réduction d'impôt ne peut pas dépasser
          l'impôt à payer, et elle n'est pas restituée. Une personne peu ou non imposable
          n'en tire rien, ou moins que le maximum. */
  function avantageFiscal(fraisMensuels, s, nbRes) {
    const mois = Math.max(0, Math.min(12, s.moisAnnee == null ? 12 : s.moisAnnee));
    const plafondDepenses = BAREME.irPlafond * nbRes * (mois / 12);
    const plafondReduction = plafondDepenses * BAREME.irTaux;
    const depenses = Math.max(0, fraisMensuels) * mois;
    const retenues = Math.min(depenses, plafondDepenses);
    const reduction = retenues * BAREME.irTaux;
    return {
      applicable: s.imposable === true,
      moisRetenus: mois,
      depenses,                         // frais engagés sur la période
      retenues,                         // part retenue après plafond
      plafondDepenses,
      plafondReduction,
      reduction: s.imposable ? reduction : 0,
      plafonne: depenses > plafondDepenses + 0.01,
      // le montant d'impôt dû n'est pas demandé : l'avantage reste un maximum théorique
      certitude: s.imposable ? 'potentiel' : 'sans objet',
    };
  }

  function calcule(e, s) {"""
)

# ── l'état : portée de l'aide au logement et durée du séjour dans l'année
rem(
    "    aideLogement: 0, imposable: false, chambre: 'cs', enfants: 0, tmi: 30,",
    """    aideLogement: 0, imposable: false, chambre: 'cs', enfants: 0, tmi: 30,
    // une aide au logement est notifiée POUR UN établissement : elle ne vaut pas partout
    aplPortee: 'cet',        // 'cet' = pour l'établissement indiqué · 'partout' = hypothèse
    aplEtab: null,           // FINESS de l'établissement pour lequel elle est notifiée
    moisAnnee: 12,           // mois passés en établissement sur l'année fiscale"""
)

io.open(P, 'w', encoding='utf-8').write(s)
print('%d blocs posés' % n)
