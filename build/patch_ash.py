# -*- coding: utf-8 -*-
"""Scénario d'aide sociale : retrait de la créance successorale présentée comme certaine,
et prise en charge du cas « tarif ASH connu, prix ordinaire absent »."""
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


# ── 1. Un établissement dont seul le tarif ASH est connu n'est plus « sans prix »
rem(
    """    if (pj == null) return { prixConnu: false, notes: ['Cet établissement n’a pas communiqué son prix. Impossible de calculer ce qu’il vous coûterait : appelez-le pour le connaître.'] };""",
    """    if (pj == null) {
      // Le tarif « aide sociale » peut exister sans le tarif ordinaire : c'est une
      // information utile, il ne faut pas présenter l'établissement comme dépourvu de prix.
      const tarifAsh = e[C.pa];
      return {
        prixConnu: false,
        tarifAshSeul: tarifAsh != null ? tarifAsh : null,
        notes: [tarifAsh != null
          ? 'Tarif aide sociale disponible (' + euro2(tarifAsh) + '/jour) ; tarif hors aide sociale non renseigné. '
            + 'Le reste à charge ordinaire ne peut donc pas être calculé : demandez le prix à l’établissement.'
          : 'Cet établissement n’a pas communiqué son prix. Impossible de calculer ce qu’il vous coûterait : appelez-le pour le connaître.'],
      };
    }"""
)

# ── 2. Le scénario ASH : ses hypothèses deviennent visibles, la créance cesse d'être certaine
rem(
    """            ${r.ash.reste > 0
              ? `<p class="f-note">Soit <b>${euro(r.ash.reste * 12)}</b> par an, <b>${euro(r.ash.reste * 36)}</b> sur trois ans.
                 C’est cette somme, cumulée sur toute la durée du séjour, que le département réclamera à la succession.</p>`
              : `<p class="f-note">Les ressources de votre parent couvrent ce prix&nbsp;: le département n’avance rien,
                 et il n’y a donc rien à récupérer sur la succession. L’aide sociale reste utile pour une raison&nbsp;:
                 elle oblige l’établissement à appliquer ce tarif-là.</p>`}""",
    """            ${r.ash.reste > 0
              ? `<p class="f-note">Ce montant s’accumule tant que dure le séjour, à raison de
                 <b>${euro(r.ash.reste * 12)} par an</b> au rythme actuel. Le département peut en
                 demander tout ou partie&nbsp;: aux enfants au titre de l’obligation alimentaire pendant
                 le séjour, et à la succession ensuite.</p>
                 <p class="att">Ce n’est pas une créance calculable d’avance. Elle dépend de la durée réelle
                 du séjour, de l’évolution des tarifs et des ressources, des montants que le département
                 fixera, et de ce que comportera la succession. Nous ne projetons donc aucun total.</p>`
              : `<p class="f-note">Au tarif retenu, les ressources de votre parent couvrent le prix&nbsp;:
                 le département n’aurait rien à avancer, donc rien à récupérer. L’aide sociale garde
                 un intérêt&nbsp;: elle ouvre l’accès au tarif habilité, souvent inférieur.</p>`}"""
)

# ── 3. Les hypothèses du scénario, affichées avec lui
rem(
    """            <p class="att">Le département peut aussi demander une participation aux enfants, et aux
            gendres et belles-filles. Aucun barème national n’existe&nbsp;: c’est lui, ou le juge, qui
            fixe les montants. <a href="/aides-ehpad/aide-sociale-hebergement/">Ce qu’il faut savoir avant de demander l’aide sociale</a></p>""",
    """            <p class="att">Le département peut aussi demander une participation aux enfants, et aux
            gendres et belles-filles. Aucun barème national n’existe&nbsp;: c’est lui, ou le juge, qui
            fixe les montants. <a href="/aides-ehpad/aide-sociale-hebergement/">Ce qu’il faut savoir avant de demander l’aide sociale</a></p>
            <details class="t-det f-hyp"><summary>Ce que ce scénario suppose</summary>
              <ul class="q-app">
                <li>Que l’aide sociale soit <b>accordée</b>&nbsp;: elle ne l’est pas de droit. Le département
                    vérifie les ressources, l’épargne, le patrimoine et la résidence.</li>
                <li>Qu’une <b>place habilitée</b> soit libre. L’habilitation de l’établissement ne garantit
                    pas que la place proposée le soit.</li>
                <li>${r.ash.prixEstime
                    ? 'Que le tarif aide sociale, <b>non communiqué</b> par cet établissement, soit proche de son tarif habituel. Le département fixe le vrai montant.'
                    : 'Que le tarif aide sociale déclaré reste celui qui sera appliqué.'}</li>
                <li>Que les ressources saisies correspondent à celles que le département retiendra&nbsp;:
                    ses règles ne recouvrent pas exactement la notion courante de revenu.</li>
              </ul>
              <p class="f-note">Ce calcul n’est pas une notification d’aide sociale. Seul le département
              en délivre une, après instruction du dossier.</p>
            </details>"""
)

io.open(P, 'w', encoding='utf-8').write(s)
print('%d blocs corrigés' % n)
