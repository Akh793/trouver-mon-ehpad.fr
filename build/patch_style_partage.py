# -*- coding: utf-8 -*-
"""La case « joindre la situation » déformait la barre de résultats.

Elle avait été posée DANS `.t-a`, un conteneur flex : son texte sur trois lignes
étirait les boutons frères sur toute la hauteur (align-items vaut stretch par
défaut), d'où des pilules géantes. Sa couleur `--mut` était en outre illisible
sur le fond bleu de la carte de total.

Correction : la case sort du conteneur des boutons et prend une couleur lisible
sur fond bleu. `.t-a` reçoit `align-items:center` pour qu'un futur ajout ne
puisse plus jamais réétirer les boutons.
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


patch('index.template.html', [
    ("""            <button type="button" id="share-btn" class="btn-sec">🔗 Copier le lien</button>
            <label class="share-opt"><input type="checkbox" id="share-situation">
              Joindre la situation saisie (ressources, autonomie) — le lien n’est pas chiffré</label>
          </div>""",
     """            <button type="button" id="share-btn" class="btn-sec">🔗 Copier le lien</button>
          </div>
          <label class="share-opt print-hide"><input type="checkbox" id="share-situation">
            <span>Joindre au lien la situation saisie — ressources et autonomie. Le lien est encodé, pas chiffré.</span></label>"""),
])

patch('site.css', [
    # les boutons ne suivent plus la hauteur de leurs voisins
    (".t-a{margin-top:1.1rem;display:flex;flex-wrap:wrap;gap:.6rem}",
     ".t-a{margin-top:1.1rem;display:flex;flex-wrap:wrap;gap:.6rem;align-items:center}"),
    # la case vit sur le fond bleu de la carte de total : couleur et taille adaptées
    ("""/* option de partage : la case doit se lire avec le bouton, pas ailleurs */
.share-opt{display:flex;gap:.4rem;align-items:flex-start;font-size:.76rem;color:var(--mut);max-width:34ch;line-height:1.35;cursor:pointer}
.share-opt input{margin-top:.15rem;flex:0 0 auto}""",
     """/* option de partage : posée SOUS les boutons, jamais dans leur rangée flex —
   un texte multiligne y étirerait les boutons voisins sur toute sa hauteur. */
.share-opt{display:flex;gap:.45rem;align-items:center;margin-top:.65rem;
  font-size:.78rem;line-height:1.3;color:rgba(255,255,255,.82);cursor:pointer;max-width:56ch}
.share-opt input{flex:0 0 auto;margin:0;accent-color:#fff;cursor:pointer}
.share-opt:hover{color:#fff}
@media (max-width:560px){.share-opt{align-items:flex-start}.share-opt input{margin-top:.15rem}}"""),
])

print('%d blocs corrigés' % n)
