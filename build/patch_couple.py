# -*- coding: utf-8 -*-
"""Couples : les ressources du résident et celles de son conjoint cessent d'être confondues.

Le formulaire demande « Retraites et pensions du parent » — donc les ressources du
résident seul. Le calcul de l'APA les divisait pourtant par deux dès que la case
« en couple » était cochée, alors que la règle divise les ressources DU MÉNAGE.
Pour un couple dont le conjoint a ses propres revenus, l'APA ressortait donc trop
élevée, et le reste à charge trop bas.
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


# ── 1. Trois notions distinctes de ressources, nommées séparément
rem(
    "  function ressourcesTotales(s) { return (Number.isFinite(s.revenus) ? s.revenus : 0) + (s.autres || 0); }",
    """  /* ---------- Trois notions de ressources, à ne jamais confondre ----------
     personne  : ce que perçoit le résident lui-même. C'est sur elles que porte sa
                 contribution à l'aide sociale (90 %), et son minimum de reste à vivre.
     conjoint  : ce que perçoit son conjoint. Saisi à part, jamais déduit du reste.
     ménage    : la somme des deux. C'est elle, divisée par deux, que le barème de
                 l'APA retient pour un couple — pas les ressources du résident seul. */
  function ressourcesPersonne(s) { return (Number.isFinite(s.revenus) ? s.revenus : 0) + (s.autres || 0); }
  function ressourcesConjoint(s) { return s.couple ? Math.max(0, s.revenusConjoint || 0) : 0; }
  function ressourcesMenage(s) { return ressourcesPersonne(s) + ressourcesConjoint(s); }
  /** Base de ressources du barème APA : le ménage divisé par deux pour un couple. */
  function ressourcesApa(s) {
    return (s.couple || s.deuxResidents) ? ressourcesMenage(s) : ressourcesPersonne(s);
  }
  /** Ressources qui font face à la facture calculée ici : celles des personnes hébergées. */
  function ressourcesTotales(s) { return s.deuxResidents ? ressourcesMenage(s) : ressourcesPersonne(s); }"""
)

# ── 2. L'APA reçoit la base du ménage, pas celle du résident seul
rem(
    "        const r = apaEtablissement(tg * mois, t56 * mois, ressourcesTotales(s), s.couple || s.deuxResidents);",
    """        // apaEtablissement divise lui-même par deux lorsque le couple est signalé :
        // on lui passe donc le TOTAL du ménage, jamais les ressources du résident seul.
        const r = apaEtablissement(tg * mois, t56 * mois, ressourcesApa(s), s.couple || s.deuxResidents);"""
)

# ── 3. L'état : les ressources du conjoint ont leur propre champ
rem(
    "    couple: false, conjointDomicile: false, deuxResidents: false,",
    """    couple: false, conjointDomicile: false, deuxResidents: false,
    revenusConjoint: 0,        // ressources propres du conjoint, jamais mêlées à celles du résident"""
)

# ── 4. Le résumé de situation dit ce qui a été retenu, et pour qui
rem(
    "    let t = `Situation retenue : ${gir}, ${euro(ressourcesTotales(s))} de ressources mensuelles`;",
    """    let t = `Situation retenue : ${gir}, ${euro(ressourcesPersonne(s))} de ressources mensuelles pour la personne hébergée`;
    if (s.couple && ressourcesConjoint(s) > 0) t += `, ${euro(ressourcesConjoint(s))} pour son conjoint`;"""
)

io.open(P, 'w', encoding='utf-8').write(s)
print('%d blocs corrigés' % n)
