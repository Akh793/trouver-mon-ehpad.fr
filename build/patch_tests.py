# -*- coding: utf-8 -*-
"""Mise à jour de la suite de tests sur le nouveau modèle de résultat.

Trois changements : la ligne de données passe à 46 colonnes (« reg »), l'avantage
fiscal n'est plus mensuel (r.ir disparaît au profit de r.fisc), et le régime de
financement devient un cas de test à part entière.
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


# ── 1. La ligne de test : 46 colonnes, régime de droit commun par défaut
rem(
    """    const mk = (o) => Object.assign(new Array(45).fill(null), o);
    const base = { mode: 'famille', gir: '34', revenus: 1500, autres: 0, epargne: 0, couple: false,
      deuxResidents: false, conjointDomicile: false, aideLogement: 0, imposable: false, chambre: 'cs', enfants: 0, tmi: 30 };""",
    """    // 46 colonnes depuis l'ajout du régime (C.reg = 45). Sans mention contraire,
    // les cas de test portent sur un établissement de droit commun.
    const mk = (o) => Object.assign(new Array(46).fill(null), { 45: 'classique' }, o);
    const base = { mode: 'famille', gir: '34', revenus: 1500, autres: 0, epargne: 0, couple: false,
      deuxResidents: false, conjointDomicile: false, aideLogement: 0, imposable: false, chambre: 'cs', enfants: 0, tmi: 30,
      aplPortee: 'partout', aplEtab: null, moisAnnee: 12 };"""
)

# ── 2. L'avantage fiscal : annuel, plafonné, et jamais retranché du mensuel
rem(
    """      ['Réduction d’impôt plafonnée à 2 500 €/an pour un résident', () =>
        Math.abs(calcule(E, { ...base, imposable: true }).ir - (0.25 * 10000) / 12) < 0.01],
      ['Deux résidents hébergés : double plafond de réduction d’impôt', () =>
        Math.abs(calcule(E, { ...base, imposable: true, deuxResidents: true }).ir - (0.25 * 20000) / 12) < 0.01],""",
    """      ['Réduction d’impôt plafonnée à 2 500 €/an pour un résident', () =>
        Math.abs(calcule(E, { ...base, imposable: true }).fisc.reduction - 0.25 * 10000) < 0.01],
      ['Deux résidents hébergés : double plafond de réduction d’impôt', () =>
        Math.abs(calcule(E, { ...base, imposable: true, deuxResidents: true }).fisc.reduction - 0.25 * 20000) < 0.01],
      ['L’avantage fiscal ne diminue pas la somme à sortir chaque mois', () =>
        calcule(E, { ...base, imposable: true }).decaisse === calcule(E, { ...base, imposable: false }).decaisse],
      ['Séjour de 5 mois : plafond de dépenses proratisé', () => {
        const f = calcule(E, { ...base, imposable: true, moisAnnee: 5 }).fisc;
        return Math.abs(f.plafondDepenses - 10000 * 5 / 12) < 0.01 && f.moisRetenus === 5;
      }],
      ['Frais sous le plafond : la réduction suit les frais, pas le plafond', () => {
        const f = calcule(mk({ 6: 20, 9: 21.85, 10: 13.86, 11: 5.89, 20: 1 }), { ...base, revenus: 6000, imposable: true }).fisc;
        return f.plafonne === false && Math.abs(f.reduction - f.depenses * 0.25) < 0.01;
      }],""",
)
rem(
    """      ['Non imposable → aucune réduction d’impôt', () => calcule(E, { ...base }).ir === 0],""",
    """      ['Non imposable → aucune réduction d’impôt', () => {
        const f = calcule(E, { ...base }).fisc;
        return f.reduction === 0 && f.applicable === false;
      }],"""
)

# ── 3. Les trois montants sont distincts et se déduisent l'un de l'autre
rem(
    """      ['Aucune extrapolation de places libres n’est produite', () => {""",
    """      ['Facture, décaissement et reste à charge sont cohérents', () => {
        const r = calcule(E, { ...base, revenus: 6000, aideLogement: 200 });
        return Math.abs(r.facture - (r.heberg + r.dependance)) < 0.01
            && Math.abs(r.decaisse - (r.facture - r.apa - r.apl)) < 0.01
            && r.rac === r.decaisse && r.total === r.facture;
      }],
      ['Régime expérimental : forfait journalier, aucune APA', () => {
        const X = mk({ 6: 100, 9: 6.10, 10: 6.10, 11: 6.10, 20: 1, 45: 'exp' });
        const r = calcule(X, { ...base });
        const pf = participationForfaitaire();
        return r.reg === 'exp' && r.apa === 0 && r.apaConnue === false
            && Math.abs(r.dependance - pf.montant * mois) < 0.01 && r.pfJour === pf.montant;
      }],
      ['Régime expérimental : le forfait ne dépend ni du GIR ni des ressources', () => {
        const X = mk({ 6: 100, 9: 21.85, 10: 13.86, 11: 5.89, 20: 1, 45: 'exp' });
        const a = calcule(X, { ...base, gir: '12', revenus: 900 });
        const b2 = calcule(X, { ...base, gir: '56', revenus: 9000 });
        return Math.abs(a.dependance - b2.dependance) < 0.01;
      }],
      ['Régime expérimental : un tarif déclaré divergent est signalé, pas retenu', () => {
        const X = mk({ 6: 100, 9: 6.10, 10: 6.10, 11: 6.10, 20: 1, 45: 'exp' });
        const r = calcule(X, { ...base });
        return r.notes.some((t) => t.indexOf('montant national en vigueur') >= 0);
      }],
      ['Régime inconnu : la part « aide au quotidien » n’est pas inventée', () => {
        const X = mk({ 6: 100, 9: 21.85, 10: 13.86, 11: 5.89, 20: 1, 45: null });
        const r = calcule(X, { ...base });
        return r.reg === 'inconnu' && r.dependance === 0 && r.depConnue === false
            && r.notes.some((t) => t.indexOf('régime de financement') >= 0);
      }],
      ['Forfait : le barème est daté et sourcé', () => {
        const a = participationForfaitaire('2025-08-01'), b2 = participationForfaitaire('2026-03-01');
        return a.montant === 6.10 && b2.montant === 6.16 && !!a.src && !!b2.src;
      }],
      ['Aide au logement notifiée pour un autre établissement : non déduite', () => {
        const r = calcule(E, { ...base, aideLogement: 300, aplPortee: 'cet', aplEtab: 'AUTRE' });
        return r.apl === 0;
      }],
      ['Tarif aide sociale seul : l’information est conservée, le calcul ne l’est pas', () => {
        const r = calcule(mk({ 9: 20, 10: 13, 11: 5, 20: 1, 21: 55 }), { ...base });
        return r.prixConnu === false && r.tarifAshSeul === 55;
      }],
      ['Aucune extrapolation de places libres n’est produite', () => {"""
)

io.open(P, 'w', encoding='utf-8').write(s)
print('%d blocs de test mis à jour' % n)
