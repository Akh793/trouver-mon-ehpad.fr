# -*- coding: utf-8 -*-
"""La part « aide au quotidien » de la facture était conditionnée à l'existence de l'APA.
Dans les territoires d'expérimentation l'APA n'existe plus, mais la participation forfaitaire
est bien facturée : elle disparaissait donc du détail, alors qu'elle figure dans le total.
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
    """    if (r.apaConnue) {
      h += l(`L’aide aux gestes du quotidien${n}`, euro(r.dependance) + '/mois');
      h += `<p class="f-note">Se lever, se laver, s’habiller, manger. Le montant dépend du niveau
        d’autonomie&nbsp;: ici le GIR&nbsp;${gir}${s.gir === '?' ? ', retenu faute de mieux' : ''}.</p>`;
      h += l('<b>Total facturé</b>', '<b>' + euro(r.total) + '/mois</b>', 'sstot');
    }""",
    """    if (r.depConnue && r.reg === 'exp') {
      h += l(`L’aide aux gestes du quotidien${n}`, euro(r.dependance) + '/mois');
      h += `<p class="f-note">Se lever, se laver, s’habiller, manger. Dans ce territoire, cette part
        est une <b>participation forfaitaire</b> de ${euro2(r.pfJour)} par jour&nbsp;: la même pour tous,
        quel que soit le niveau d’autonomie et quelles que soient les ressources.</p>`;
      h += l('<b>Total facturé</b>', '<b>' + euro(r.total) + '/mois</b>', 'sstot');
    } else if (r.depConnue) {
      h += l(`L’aide aux gestes du quotidien${n}`, euro(r.dependance) + '/mois');
      h += `<p class="f-note">Se lever, se laver, s’habiller, manger. Le montant dépend du niveau
        d’autonomie&nbsp;: ici le GIR&nbsp;${gir}${s.gir === '?' ? ', retenu faute de mieux' : ''}.</p>`;
      h += l('<b>Total facturé</b>', '<b>' + euro(r.total) + '/mois</b>', 'sstot');
    } else {
      h += l(`L’aide aux gestes du quotidien${n}`, 'non calculée');
      h += `<p class="f-note">Cette part de la facture existe, mais nous ne disposons pas de
        l’information nécessaire pour la chiffrer ici. Le total ci-dessous est donc incomplet.</p>`;
    }"""
)

# Le bloc « ce que les aides retirent » doit expliquer l'absence d'APA quand elle est supprimée
rem(
    """    } else if (r.apaConnue) {
      h += '<h4 class="f-t1">Ce que les aides retirent</h4>';
      h += r.notes.length
        ? '<p class="f-note">Aucune aide n’a pu être déduite, pour la raison suivante&nbsp;:</p>'
        : `<p class="f-note">Aucune aide n’a pu être déduite. Les ressources indiquées dépassent
           les plafonds, ou aucune aide n’a été saisie.</p>`;
    }""",
    """    } else if (r.reg === 'exp') {
      h += '<h4 class="f-t1">Ce que les aides retirent</h4>';
      h += `<p class="f-note">Aucune. Dans ce territoire, l’APA en établissement est <b>supprimée</b>
        depuis le 1<sup>er</sup> juillet 2025&nbsp;: il n’y a plus d’aide à déduire, parce qu’il n’y a
        plus de participation à moduler. La participation forfaitaire ci-dessus en tient lieu.
        L’aide au logement, elle, reste due si votre parent y a droit.</p>`;
    } else if (r.apaConnue) {
      h += '<h4 class="f-t1">Ce que les aides retirent</h4>';
      h += r.notes.length
        ? '<p class="f-note">Aucune aide n’a pu être déduite, pour la raison suivante&nbsp;:</p>'
        : `<p class="f-note">Aucune aide n’a pu être déduite. Les ressources indiquées dépassent
           les plafonds, ou aucune aide n’a été saisie.</p>`;
    }"""
)

io.open(P, 'w', encoding='utf-8').write(s)
print('%d blocs corrigés' % n)
