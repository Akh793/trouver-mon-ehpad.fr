# -*- coding: utf-8 -*-
"""Refonte rédactionnelle — lot 6 : les démarches et le partage.

Chaque recherche produisait huit à dix articles complets — étapes, pièces,
avertissements, listes de visite — soit plus de mille mots déroulés d'un bloc.
Trois actions prioritaires restent visibles ; les autres passent derrière
« Toutes les démarches ». Aucun contenu n'est perdu.

Le partage remplace « encodé, pas chiffré » — une notion technique — par sa
conséquence : qui pourra lire quoi.
"""
import io, os, sys

B = os.path.dirname(os.path.abspath(__file__))
n = 0


def patch(rel, paires):
    global n
    p = os.path.join(B, rel)
    s = io.open(p, encoding='utf-8').read()
    for a, b in paires:
        if a not in s:
            print('INTROUVABLE dans %s :' % rel, a[:110].replace('\n', ' '))
            sys.exit(1)
        s = s.replace(a, b, 1)
        n += 1
    io.open(p, 'w', encoding='utf-8').write(s)


patch(os.path.join('..', 'site', 'app.js'), [
    ("""    return keys.map((k, i) => {
      const rm = ROADMAPS[k];
      return `<article class="step">""",
     """    // Trois démarches ouvertes, le reste replié : dérouler dix articles complets
    // après chaque recherche noie l'action à faire en premier.
    const carte = (k, i) => {
      const rm = ROADMAPS[k];
      return `<article class="step">"""),

    ("""        ${rm.warnings.length ? `<div class="piege">${rm.warnings.map(esc).join('<br>')}</div>` : ''}
      </article>`;
    }).join('');
  }""",
     """        ${rm.warnings.length ? `<div class="piege">${rm.warnings.map(esc).join('<br>')}</div>` : ''}
      </article>`;
    };
    const tete = keys.slice(0, 3).map(carte).join('');
    const reste = keys.slice(3);
    return tete + (reste.length
      ? `<details class="bloc-plus route-plus"><summary><b>Toutes les démarches</b>
          <span>— ${reste.length} autre${reste.length > 1 ? 's' : ''} étape${reste.length > 1 ? 's' : ''}</span></summary>
          ${reste.map((k, i) => carte(k, i + 3)).join('')}</details>`
      : '');
  }"""),

    # ── Le partage : la conséquence, pas le vocabulaire technique
    ("""    const quoi = avec
      ? 'Il contient la situation saisie — ressources, épargne, niveau d’autonomie — en clair : '
        + 'l’adresse est encodée, pas chiffrée. Ne l’envoyez qu’à des personnes concernées.'
      : 'Il rouvre la recherche (commune, rayon, filtres) sans aucune information sur les ressources '
        + `ni sur ${mot('autonomie')}.`;""",
     """    const quoi = avec
      ? 'Les destinataires pourront lire les revenus et le niveau d’autonomie ajoutés au lien.'
      : 'Il rouvre la recherche seule : ni revenus, ni niveau d’autonomie.';"""),
])

patch('index.template.html', [
    ("""      <h2><span class="n">3</span> Votre mode <em class="co">d’emploi</em></h2>""",
     """      <h2><span class="n">3</span> Préparer les <em class="co">prochaines étapes</em></h2>"""),
    ("""    <div id="route-vide" class="vide"><p class="v-s">Les démarches à faire, dans l’ordre, avec les pièces à préparer et les pièges documentés, apparaîtront ici.</p></div>""",
     """    <div id="route-vide" class="vide"><p class="v-s">Les démarches à engager apparaîtront ici, dans l’ordre, avec les pièces à préparer.</p></div>"""),
    ("""            <label class="share-opt print-hide"><input type="checkbox" id="share-situation">
            <span>Joindre la situation saisie au lien — il est encodé, pas chiffré</span></label>""",
     """            <label class="share-opt print-hide"><input type="checkbox" id="share-situation">
            <span>Joindre ma situation au lien — les destinataires pourront la lire</span></label>"""),
    ("""      <button type="button" id="print-btn" class="btn" data-print>🖨️ Imprimer ou enregistrer ma fiche</button>""",
     """      <button type="button" id="print-btn" class="btn-sec" data-print>Imprimer</button>"""),
])

print('%d blocs posés' % n)
