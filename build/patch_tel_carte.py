# -*- coding: utf-8 -*-
"""Le numéro de l'établissement remonte sur la carte de résultat.

Tout le produit dit la même chose sur la disponibilité : aucune source publique ne
la publie, seul l'établissement peut répondre. Le numéro était pourtant enfoui dans
un onglet de la fiche. Il rejoint la rangée d'actions, au même niveau que « Voir la
fiche », « Comparer » et « Garder ».

Un lien `tel:` posé dans une carte cliquable doit interrompre la propagation :
sans cela, le clic déclenche à la fois l'appel et l'ouverture de la fiche.
"""
import io, os, sys

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site', 'app.js')
C = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site.css')
n = 0


def patch(chemin, paires):
    global n
    s = io.open(chemin, encoding='utf-8').read()
    for a, b in paires:
        if a not in s:
            print('INTROUVABLE dans %s :' % os.path.basename(chemin), a[:110].replace('\n', ' '))
            sys.exit(1)
        s = s.replace(a, b, 1)
        n += 1
    io.open(chemin, 'w', encoding='utf-8').write(s)


patch(P, [
    # ── le formatage du numéro, écrit une fois pour les deux usages
    ("  const nom = (e) => (e[C.nom] || '').replace(/\\s+/g, ' ').trim();",
     """  const nom = (e) => (e[C.nom] || '').replace(/\\s+/g, ' ').trim();
  /** 0478602323 → 04 78 60 23 23 : un numéro se lit par paires, et se compose mieux. */
  const telFr = (t) => String(t || '').replace(/\\D/g, '').replace(/(\\d\\d)(?=\\d)/g, '$1 ');"""),

    # ── le lien dans la rangée d'actions
    ("""        <button type="button" class="mini2 fav ${fav ? 'on' : ''}" data-fav="${fin}" aria-pressed="${fav}" title="Garder pour plus tard">${fav ? '♥ Gardé' : '♡ Garder'}</button>""",
     """        <button type="button" class="mini2 fav ${fav ? 'on' : ''}" data-fav="${fin}" aria-pressed="${fav}" title="Garder pour plus tard">${fav ? '♥ Gardé' : '♡ Garder'}</button>
        ${e[C.tel] ? `<a class="mini2 res-tel" data-tel href="tel:${esc(String(e[C.tel]).replace(/\\D/g, ''))}"
             title="Seul l’établissement peut dire si une place est libre">☎ ${esc(telFr(e[C.tel]))}</a>` : ''}"""),

    # ── le clic ne doit pas ouvrir la fiche en même temps qu'il compose
    ("""    const carte = t.closest('.res');
    if (carte) { selectionne(carte.dataset.fin); return; }""",
     """    // Le lien téléphone vit dans une carte cliquable : sans cette interception,
    // le clic composerait le numéro ET ouvrirait la fiche derrière.
    const tel = t.closest('[data-tel]');
    if (tel) { e.stopPropagation(); evt('tel_clicked', {}); return; }
    const carte = t.closest('.res');
    if (carte) { selectionne(carte.dataset.fin); return; }"""),
])

patch(C, [
    (".res-fin{font-size:.68rem",
     """/* Le numéro reste un lien, pas un bouton : il agit hors de la page. */
.res-tel{color:var(--bl-t);border-color:var(--bd-bl2,var(--bd));text-decoration:none;
  font-variant-numeric:tabular-nums;white-space:nowrap}
.res-tel:hover{background:var(--ti-bl);border-color:var(--bl-t)}
.res-fin{font-size:.68rem"""),
])

print('%d blocs posés' % n)
